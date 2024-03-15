<script lang="ts">
import { Ref, computed, h, inject, provide, ref, watch } from "vue";
import { getTemplate } from "../core/templateMap";
import {
	Component,
	InstancePath,
	InstancePathItem,
	UserFunction,
} from "../streamsyncTypes";
import ComponentProxy from "./ComponentProxy.vue";
import { useEvaluator } from "./useEvaluator";
import injectionKeys from "../injectionKeys";
import { VNode } from "vue";
import ChildlessPlaceholder from "./ChildlessPlaceholder.vue";

export default {
	props: ["componentId", "instancePath", "instanceData", "renderOnly"],
	setup(props) {
		const ss = inject(injectionKeys.core);
		const ssbm = inject(injectionKeys.builderManager);
		const componentId: Component["id"] = props.componentId;
		const component = computed(() => ss.getComponentById(componentId));
		const componentDefinition = ss.getComponentDefinitionById(componentId);
		const allowedSlots = computed(() => [
			...(componentDefinition.value.allowedSlots || []),
			"default",
		]);
		const template = getTemplate(component.value.type);
		const instancePath: InstancePath = props.instancePath;
		const instanceData = props.instanceData;
		const { getEvaluatedFields, isComponentVisible } = useEvaluator(ss);
		const evaluatedFields = getEvaluatedFields(instancePath);

		const children = computed(() => ss.getComponents(componentId, true));
		const isBeingEdited = computed(
			() => !!ssbm && ssbm.getMode() != "preview",
		);
		const isDisabled = ref(false);
		const userFunctions: Ref<UserFunction[]> = computed(() =>
			ss.getUserFunctions(),
		);

		const getChildlessPlaceholderVNode = (): VNode => {
			if (children.value.length > 0) return;
			return h(ChildlessPlaceholder, {
				componentId: component.value.id,
			});
		};

		const renderProxiedComponent = (
			componentId: Component["id"],
			instanceNumber: InstancePathItem["instanceNumber"] = 0,
			ext: { class?: string } = {},
		) => {
			const vnode = h(ComponentProxy, {
				componentId,
				key: `${componentId}:${instanceNumber}`,
				instancePath: [
					...instancePath,
					{
						componentId: componentId,
						instanceNumber,
					},
				],
				instanceData: [...instanceData, ref(null)],
				...ext,
				renderOnly: props.renderOnly || ext.renderOnly,
			});
			return vnode;
		};

		const getValidSlot = (childId: Component["id"]): string => {
			const childDef = ss.getComponentDefinitionById(childId);
			const slot = childDef.value.slot ?? "default";
			return allowedSlots.value.includes(slot) ? slot : "default";
		};

		const getChildrenVNodes = (
			instanceNumber: InstancePathItem["instanceNumber"] = 0,
			slotName: string = "default",
			componentFilter: (c: Component) => boolean = () => true,
			positionlessSlot: boolean = false,
		): VNode[] => {
			const renderInsertionSlot = (position: number) => {
				return h("div", {
					"data-streamsync-slot-of-id": componentId,
					"data-streamsync-position": position,
				});
			};
			const showSlots = isBeingEdited.value && !positionlessSlot;

			const childrenVNodes = children.value
				.map((c) => ({ ...c, slot: getValidSlot(c.id) }))
				.filter(
					(c: Component & { slot: string }) => c.slot === slotName,
				)
				.filter((c) => componentFilter(c))
				.map((childComponent, childIndex) => {
					const childVNode = renderProxiedComponent(
						childComponent.id,
						instanceNumber,
					);
					return [
						childVNode,
						...(showSlots
							? [renderInsertionSlot(childIndex + 1)]
							: []),
					];
				});

			return [...(showSlots ? [renderInsertionSlot(0)] : [])].concat(
				childrenVNodes.flat(),
			);
		};

		const flattenInstancePath = (path: InstancePath) => {
			return path
				.map((ie) => `${ie.componentId}:${ie.instanceNumber}`)
				.join(",");
		};
		const flattenedInstancePath = flattenInstancePath(instancePath);

		provide(injectionKeys.evaluatedFields, evaluatedFields);
		provide(injectionKeys.componentId, componentId);
		provide(injectionKeys.isBeingEdited, isBeingEdited);
		provide(injectionKeys.isDisabled, isDisabled);
		provide(injectionKeys.instancePath, instancePath);
		provide(injectionKeys.instanceData, instanceData);
		provide(injectionKeys.renderProxiedComponent, renderProxiedComponent);
		provide(injectionKeys.getChildrenVNodes, getChildrenVNodes);
		provide(injectionKeys.flattenedInstancePath, flattenedInstancePath);

		const dataAttrs = {
			"data-streamsync-id": componentId,
			"data-streamsync-instance-path": flattenedInstancePath,
		};

		/*
		Selected stylesheet class is removed if changes are made,
		for the developer to appreciate the changes. Particularly important
		for colour changes, with which selection interferes.
		*/

		const isSelected = ref(false);
		watch(
			() => ssbm?.getSelectedId() == componentId,
			(isNowSelected) => {
				isSelected.value = isNowSelected;
			},
		);
		watch(
			() => evaluatedFields,
			() => {
				isSelected.value = false;
			},
			{ deep: true },
		);

		const isChildless = computed(() => children.value.length == 0);
		const isVisible = computed(() =>
			isComponentVisible(componentId, instancePath),
		);

		const getHandlerCallable = (
			handlerFunctionName: string,
			isBinding: boolean,
		) => {
			const isForwardable = !handlerFunctionName.startsWith("$");
			if (isForwardable && !isBinding) {
				return (ev: Event) => {
					// Only include payload if there's a function waiting for it on the other side

					let includePayload = false;

					if (
						userFunctions.value.some(
							(uf) =>
								uf.name == handlerFunctionName &&
								uf.args.includes("payload"),
						)
					) {
						includePayload = true;
					}
					ss.forwardEvent(ev, instancePath, includePayload);
				};
			}
			if (handlerFunctionName.startsWith("$goToPage_")) {
				const pageKey = handlerFunctionName.substring(
					"$goToPage_".length,
				);
				return (ev: Event) => ss.setActivePageFromKey(pageKey);
			}
			return null;
		};

		const eventHandlerProps = computed(() => {
			const props = {};

			// Handle event handlers

			const handledEventTypes = Object.keys(
				component.value.handlers ?? {},
			);
			const boundEventTypes = component.value.binding
				? [component.value.binding.eventType]
				: [];
			const eventTypes = Array.from(
				new Set([...handledEventTypes, ...boundEventTypes]),
			);

			eventTypes.forEach((eventType) => {
				const eventKey = `on${eventType
					.charAt(0)
					.toUpperCase()}${eventType.slice(1)}`;
				const isBinding =
					eventType === component.value.binding?.eventType;
				props[eventKey] = (ev: Event) => {
					if (isBinding) {
						ss.forwardEvent(ev, instancePath, true);
					}
					const handlerFunction =
						component.value.handlers?.[eventType];
					if (handlerFunction) {
						getHandlerCallable(handlerFunction, isBinding)?.(ev);
					}
				};
			});

			return props;
		});

		const fieldBasedStyleVars = computed(() => {
			const fields = ss.getComponentDefinition(
				component.value.type,
			)?.fields;
			if (!fields) return;
			const styleVars = {};
			Object.keys(fields).forEach((key) => {
				if (!fields[key].applyStyleVariable) return;
				if (!evaluatedFields[key]) return;
				styleVars[`--${key}`] = evaluatedFields[key].value;
			});
			return styleVars;
		});

		const fieldBasedCssClasses = computed(() => {
			const CSS_CLASSES_FIELD_KEY = "cssClasses";
			const fields = ss.getComponentDefinition(
				component.value.type,
			)?.fields;
			if (!fields) return;
			if (
				!fields[CSS_CLASSES_FIELD_KEY] ||
				!evaluatedFields[CSS_CLASSES_FIELD_KEY]
			)
				return;
			const cssStr: string = evaluatedFields[CSS_CLASSES_FIELD_KEY].value;
			const cssClassesArr = cssStr?.split(" ").map((s) => s.trim());
			const cssClasses = {};
			cssClassesArr.forEach((key) => {
				cssClasses[key] = true;
			});
			return cssClasses;
		});

		const getRootElProps = function () {
			const rootElProps = {
				class: {
					component: true,
					childless: isChildless.value,
					selected: isSelected.value,
					disabled: isDisabled.value,
					beingEdited: isBeingEdited.value,
					...fieldBasedCssClasses.value,
				},
				style: {
					...fieldBasedStyleVars.value,
					...(!isVisible.value ? { display: "none" } : {}),
				},
				...dataAttrs,
				...(!isDisabled.value ? eventHandlerProps.value : []),
				draggable: !props.renderOnly && isBeingEdited.value,
			};
			return rootElProps;
		};

		return () => {
			const childlessPlaceholder = isBeingEdited.value
				? getChildlessPlaceholderVNode()
				: undefined;

			const defaultSlotFn = ({
				instanceNumber = 0,
				slotName = "default",
				componentFilter = () => true,
				positionlessSlot = false,
			}: {
				instanceNumber: number;
				slotName: string;
				componentFilter: (c: Component) => boolean;
				positionlessSlot: boolean;
			}) => {
				if (isChildless.value) {
					return positionlessSlot ? undefined : childlessPlaceholder;
				}
				const vnodes = getChildrenVNodes(
					instanceNumber,
					slotName,
					componentFilter,
					positionlessSlot,
				);
				return vnodes;
			};

			const vnodeProps = {
				...getRootElProps(),
			};
			const renderedComponent = h(template, vnodeProps, {
				default: defaultSlotFn,
			});

			return renderedComponent;
		};
	},
};
</script>
<style scoped>
@import "../renderer/sharedStyles.css";
</style>
