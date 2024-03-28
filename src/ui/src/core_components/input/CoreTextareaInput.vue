<template>
	<div ref="rootEl" class="CoreTextareaInput">
		<label>{{ fields.label.value }}</label>
		<textarea
			:value="formValue"
			:placeholder="fields.placeholder.value"
			:rows="fields.rows.value"
			@input="
				($event) =>
					handleInput(
						($event.target as HTMLTextAreaElement).value,
						'ss-change',
					)
			"
			@change="
				($event) =>
					handleInput(
						($event.target as HTMLTextAreaElement).value,
						'ss-change-finish',
					)
			"
		></textarea>
	</div>
</template>

<script lang="ts">
import { FieldControl, FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const description =
	"A user input component that allows users to enter multi-line text values.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "new_val" to the new value

	state["new_val"] = payload`;

export default {
	streamsync: {
		name: "Textarea Input",
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
				control: FieldControl.Textarea,
			},
			rows: {
				name: "Rows",
				type: FieldType.Number,
				init: "5",
				default: "5",
			},
			cssClasses,
		},
		events: {
			"ss-change": {
				desc: "Capture changes as they happen.",
				stub: onChangeHandlerStub,
				bindable: true,
			},
			"ss-change-finish": {
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
const ss = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker(ss, instancePath, rootEl);
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreTextareaInput {
	max-width: 70ch;
	width: 100%;
}

label {
	display: block;
	margin-bottom: 8px;
	color: var(--primaryTextColor);
}

textarea {
	width: 100%;
	margin: 0;
	border: 1px solid var(--separatorColor);
	resize: vertical;
}
</style>
