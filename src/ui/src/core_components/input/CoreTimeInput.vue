<template>
	<BaseInputWrapper
		ref="rootInstance"
		:label="fields.label.value"
		class="CoreTimeInput"
	>
		<input
			type="time"
			:value="formValue"
			@change="
				($event) =>
					handleInput(
						($event.target as HTMLInputElement).value,
						'wf-time-change',
					)
			"
		/>
	</BaseInputWrapper>
</template>

<script lang="ts">
import { ComponentPublicInstance } from "vue";
import { cssClasses } from "../../renderer/sharedStyleFields";
import { FieldType } from "../../writerTypes";
import BaseInputWrapper from "../base/BaseInputWrapper.vue";

const description =
	"A user input component that allows users to select a time.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "new_time" to the new value, provided as a hh:mm string (in 24-hour format that includes leading zeros).

	state["new_time"] = payload`;

export default {
	writer: {
		name: "Time Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			cssClasses,
		},
		events: {
			"wf-time-change": {
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
const rootInstance = ref<ComponentPublicInstance | null>(null);
const wf = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);

const { formValue, handleInput } = useFormValueBroker(
	wf,
	instancePath,
	rootInstance,
);
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
@import "../../renderer/colorTransformations.css";

.CoreTimeInput {
	width: fit-content;
}

input {
	width: 100%;
	max-width: 20ch;
	margin: 0;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	padding: 8.5px 12px 8.5px 12px;
	font-size: 0.875rem;
	outline: none;
}

input:focus {
	border: 1px solid var(--softenedAccentColor);
	box-shadow: 0px 0px 0px 3px rgba(81, 31, 255, 0.05);
}
</style>
