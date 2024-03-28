<template>
	<div ref="rootEl" class="CoreSliderInput">
		<label>{{ fields.label.value }}</label>
		<div class="inputArea">
			<input
				type="range"
				:value="formValue"
				:min="fields.minValue.value"
				:max="fields.maxValue.value"
				:step="fields.stepSize.value"
				@input="
					($event) =>
						handleInput(
							($event.target as HTMLInputElement).value,
							'ss-number-change',
						)
				"
			/>
			<div class="valueContainer">
				<h3>{{ formValue }}</h3>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const description =
	"A user input component that allows users to select numeric values using a slider with optional constraints like min, max, and step.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "new_val" to the new value

	state["new_val"] = payload`;

export default {
	streamsync: {
		name: "Slider Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			minValue: {
				name: "Minimum value",
				type: FieldType.Number,
				default: "0",
				init: "0",
			},
			maxValue: {
				name: "Maximum value",
				type: FieldType.Number,
				default: "100",
				init: "100",
			},
			stepSize: {
				name: "Step size",
				type: FieldType.Number,
				default: "1",
				init: "1",
			},
			cssClasses,
		},
		events: {
			"ss-number-change": {
				desc: "Capture changes to this control.",
				stub: onChangeHandlerStub,
				bindable: true,
			},
		},
	},
};
</script>

<script setup lang="ts">
import { inject, ref } from "vue";
import injectionKeys from "../../injectionKeys";
import { useFormValueBroker } from "../../renderer/useFormValueBroker";

const fields = inject(injectionKeys.evaluatedFields);
const rootEl = ref(null);
const ss = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker(ss, instancePath, rootEl);
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreSliderInput {
	width: 100%;
	max-width: 40ch;
}

label {
	display: block;
	margin-bottom: 8px;
	color: var(--primaryTextColor);
}

.inputArea {
	display: flex;
	gap: 8px;
}

input {
	flex: 1 1 auto;
	min-width: 0;
	margin: 0;
}

.valueContainer {
	min-width: 0;
	flex: 0 0 auto;
	text-align: right;
}
</style>
