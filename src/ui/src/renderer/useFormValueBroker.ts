import { computed, Ref, ref, watch } from "vue";
import { Core, InstancePath } from "../streamsyncTypes";
import { useEvaluator } from "../renderer/useEvaluator";

/**
 *
 * Encapsulates repeatable form value logic, including binding.
 *
 * @param ss
 * @param componentId
 * @returns
 */
export function useFormValueBroker(
	ss: Core,
	instancePath: InstancePath,
	emitterEl: Ref<HTMLElement>,
) {
	const formValue: Ref<any> = ref();
	const isBusy = ref(false);
	const queuedEvent: Ref<{ eventValue: any; emitEventType: string }> =
		ref(null);

	const componentId = instancePath.at(-1).componentId;
	const component = computed(() => ss.getComponentById(componentId));
	const { evaluateExpression } = useEvaluator(ss);

	function getBindingValue() {
		const component = ss.getComponentById(componentId);
		if (component?.binding?.stateRef) {
			const value = evaluateExpression(
				component.binding.stateRef,
				instancePath,
			);
			return value;
		}
		return;
	}

	/**
	 * Takes a value and emits a CustomEvent of the given type.
	 * Deals with debouncing.
	 *
	 * @param newValue
	 * @param emitEventType
	 * @returns
	 */
	function handleInput(
		eventValue: any,
		emitEventType: string,
		customCallback?: Function,
	) {
		formValue.value = eventValue;

		const isHandlerSet = component.value.handlers?.[emitEventType];
		const isBindingSet =
			component.value.binding?.eventType == emitEventType;

		// Event is not used
		if (!isHandlerSet && !isBindingSet) return;

		if (isBusy.value) {
			// Queued event is overwritten for debouncing purposes

			queuedEvent.value = {
				eventValue,
				emitEventType,
			};
			return;
		}

		isBusy.value = true;
		const callback = () => {
			isBusy.value = false;
			if (queuedEvent.value) {
				handleInput(
					queuedEvent.value.eventValue,
					queuedEvent.value.emitEventType,
				);
				queuedEvent.value = null;
			}
			customCallback?.();
		};

		const event = new CustomEvent(emitEventType, {
			detail: {
				payload: eventValue,
				callback,
			},
		});
		emitterEl.value.dispatchEvent(event);
	}

	watch(
		() => getBindingValue(),
		(value) => {
			if (isBusy.value) return;
			formValue.value = value;
		},
		{ immediate: true },
	);

	watch(
		formValue,
		(newValue) => {
			if (typeof newValue === "undefined") {
				formValue.value = "";
			}
		},
		{ immediate: true },
	);

	return {
		formValue,
		handleInput,
	};
}
