<template>
	<div ref="rootEl" class="CoreNumberInput">
		<label>{{ fields.label.value }}</label>
		<input
			ref="inputEl"
			type="number"
			:value="formValue"
			:placeholder="fields.placeholder.value"
			:min="
				fields.minValue.value !== null
					? fields.minValue.value
					: undefined
			"
			:max="
				fields.maxValue.value !== null
					? fields.maxValue.value
					: undefined
			"
			:step="
				fields.valueStep.value !== null
					? fields.valueStep.value
					: undefined
			"
			@input="handleInputEvent"
			@change="handleChangeEvent"
		/>
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const description =
	"A user input component that allows users to enter numeric values.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "new_val" to the new value

	state["new_val"] = payload`;

export default {
	streamsync: {
		name: "Number Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			placeholder: {
				name: "Placeholder",
				type: FieldType.Text,
			},
			minValue: {
				name: "Minimum value",
				type: FieldType.Number,
				default: null,
			},
			maxValue: {
				name: "Max value",
				type: FieldType.Number,
				default: null,
			},
			valueStep: {
				name: "Step",
				type: FieldType.Number,
				default: "1",
			},
			cssClasses,
		},
		events: {
			"ss-number-change": {
				desc: "Capture changes as they happen.",
				stub: onChangeHandlerStub,
				bindable: true,
			},
			"ss-number-change-finish": {
				desc: "Capture changes once this control has lost focus.",
				stub: onChangeHandlerStub,
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
const inputEl = ref(null);
const ss = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker(ss, instancePath, rootEl);

function enforceLimitsAndReturnValue() {
	if (inputEl.value.value == "") return null;

	let v: number = parseFloat(inputEl.value.value);

	if (isNaN(v)) return v;
	if (fields.minValue.value !== null && v < fields.minValue.value) {
		v = fields.minValue.value;
		inputEl.value.value = v;
	}
	if (fields.maxValue.value !== null && v > fields.maxValue.value) {
		v = fields.maxValue.value;
		inputEl.value.value = v;
	}
	return v;
}

function handleInputEvent() {
	const v = enforceLimitsAndReturnValue();
	if (isNaN(v)) return;
	handleInput(v, "ss-number-change");
}

function handleChangeEvent() {
	const v = enforceLimitsAndReturnValue();
	if (isNaN(v)) return;
	handleInput(v, "ss-number-change-finish");
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreNumberInput {
	max-width: 70ch;
	width: 100%;
}

label {
	display: block;
	margin-bottom: 8px;
	color: var(--primaryTextColor);
}

input {
	width: 100%;
	margin: 0;
	border: 1px solid var(--separatorColor);
}
</style>
