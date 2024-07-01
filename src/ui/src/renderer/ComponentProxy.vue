<script lang="ts">
import {
	PropType,
	Ref,
	VNode,
	computed,
	h,
	inject,
	provide,
	ref,
	watch,
} from "vue";
import { getTemplate } from "../core/templateMap";
import injectionKeys from "../injectionKeys";
import {
	Component,
	InstancePath,
	InstancePathItem,
	UserFunction,
} from "../writerTypes";
import ChildlessPlaceholder from "./ChildlessPlaceholder.vue";
import ComponentProxy from "./ComponentProxy.vue";
import RenderError from "./RenderError.vue";
import { flattenInstancePath } from "./instancePath";
import { useEvaluator } from "./useEvaluator";

export default {
	props: {
		componentId: { type: String, required: true },
		instancePath: { type: Array as PropType<InstancePath>, required: true },
		instanceData: { validator: () => true, required: true },
	},
	setup(props) {
		const wf = inject(injectionKeys.core);
		const ssbm = inject(injectionKeys.builderManager);
		const componentId = props.componentId;
		const component = computed(() => wf.getComponentById(componentId));
		const template = getTemplate(component.value.type);
		const instancePath = props.instancePath;
		const instanceData = props.instanceData;
		const { getEvaluatedFields, isComponentVisible } = useEvaluator(wf);
		const evaluatedFields = getEvaluatedFields(instancePath);

		const children = computed(() =>
			wf.getComponents(componentId, { sortedByPosition: true }),
		);
		const isBeingEdited = computed(
			() => !!ssbm && ssbm.getMode() != "preview",
		);
		const isDraggable = computed(
			() =>
				isBeingEdited.value &&
				!component.value.isCodeManaged &&
				component.value.type !== "root",
		);

		const isParentSuitable = (parentId, childType) => {
			const allowedTypes = !parentId
				? ["root"]
				: wf.getContainableTypes(parentId);
			return allowedTypes.includes(childType);
		};

		const isDisabled = ref(false);
		const userFunctions: Ref<UserFunction[]> = computed(() =>
			wf.getUserFunctions(),
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
			ext: { class?: string; contextSlot?: string } = {},
		): VNode => {
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
			});
			return vnode;
		};

		const filterBySlot =
			(slotName: string) =>
			(c: Component): boolean => {
				if (
					!isParentSuitable(componentId, c.type) &&
					slotName === "default"
				)
					return true;
				const childDef = wf.getComponentDefinition(c.type);
				const slot = childDef.slot ?? "default";
				return slot === "*" || slot === slotName;
			};

		const getChildrenVNodes = (
			instanceNumber: InstancePathItem["instanceNumber"] = 0,
			slotName: string = "default",
			componentFilter: (c: Component) => boolean = () => true,
			positionlessSlot: boolean = false,
		): VNode[] => {
			const renderInsertionSlot = (position: number): VNode[] => {
				if (!isBeingEdited.value || positionlessSlot) return [];
				return [
					h("div", {
						"data-writer-slot-of-id": componentId,
						"data-writer-position": position,
					}),
				];
			};

			const slotComponents = children.value
				.filter(filterBySlot(slotName))
				.filter(componentFilter);

			const bmcVNodes = slotComponents
				.filter((c) => !c.isCodeManaged)
				.map((childComponent) =>
					renderProxiedComponent(childComponent.id, instanceNumber, {
						contextSlot: slotName,
					}),
				);

			const cmcVNodes = slotComponents
				.filter((c) => c.isCodeManaged)
				.map((childComponent) =>
					renderProxiedComponent(childComponent.id, instanceNumber, {
						contextSlot: slotName,
					}),
				);

			return [
				...renderInsertionSlot(0),
				...bmcVNodes
					.map((vnode: VNode, idx): VNode[] => [
						vnode,
						renderInsertionSlot(idx + 1),
					])
					.flat(),
				...cmcVNodes,
			];
		};

		const flattenedInstancePath = flattenInstancePath(instancePath);

		provide(injectionKeys.evaluatedFields, evaluatedFields);
		provide(injectionKeys.componentId, componentId);
		provide(injectionKeys.isBeingEdited, isBeingEdited);
		provide(injectionKeys.isDisabled, isDisabled);
		provide(injectionKeys.instancePath, instancePath);
		provide(injectionKeys.instanceData, instanceData as any);
		provide(injectionKeys.renderProxiedComponent, renderProxiedComponent);
		provide(injectionKeys.getChildrenVNodes, getChildrenVNodes);
		provide(injectionKeys.flattenedInstancePath, flattenedInstancePath);

		const dataAttrs = {
			"data-writer-id": componentId,
			"data-writer-instance-path": flattenedInstancePath,
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
					wf.forwardEvent(ev, instancePath, includePayload);
				};
			}
			if (handlerFunctionName.startsWith("$goToPage_")) {
				const pageKey = handlerFunctionName.substring(
					"$goToPage_".length,
				);
				return (ev: Event) => wf.setActivePageFromKey(pageKey);
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
						wf.forwardEvent(ev, instancePath, true);
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
			const fields = wf.getComponentDefinition(
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
			const fields = wf.getComponentDefinition(
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
					[`wf-type-${component.value.type}`]: true,
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
				draggable: isDraggable.value,
			};
			return rootElProps;
		};

		const renderErrorVNode = (vnodeProps, message): VNode => {
			if (!isBeingEdited.value) return h("div");
			return h(RenderError, {
				...vnodeProps,
				componentType: component.value.type,
				message,
			});
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

			if (
				!isParentSuitable(
					component.value.parentId,
					component.value.type,
				)
			) {
				return renderErrorVNode(
					vnodeProps,
					"Parent is not suitable for this component",
				);
			}

			return h(template, vnodeProps, {
				default: defaultSlotFn,
			});
		};
	},
};
</script>
<style scoped>
@import "../renderer/sharedStyles.css";
</style>
