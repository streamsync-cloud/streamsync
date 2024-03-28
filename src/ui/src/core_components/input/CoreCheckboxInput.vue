<template>
	<div ref="rootEl" class="CoreCheckboxInput">
		<div class="mainLabel">{{ fields.label.value }}</div>
		<div
			class="options"
			:class="{
				horizontal: fields.orientation.value == 'horizontal',
			}"
		>
			<div
				v-for="(option, optionKey) in fields.options.value"
				:key="optionKey"
				class="option"
			>
				<input
					type="checkbox"
					:checked="
						Array.isArray(formValue)
							? formValue.includes(optionKey)
							: false
					"
					:value="optionKey"
					@input="
						($event) =>
							handleInput(getCheckedKeys(), 'ss-options-change')
					"
				/><label :for="`${flattenedInstancePath}-option-${optionKey}`">
					{{ option }}
				</label>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
import { computed, inject, Ref } from "vue";
import { ref } from "vue";
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const defaultOptions = { a: "Option A", b: "Option B" };

const description =
	"A user input component that allows users to choose multiple values from a list of options using checkboxes.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "selected" to the selected options.
	# The payload will be a list, as multiple options are allowed.

	state["selected"] = payload`;

export default {
	streamsync: {
		name: "Checkbox Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			options: {
				name: "Options",
				desc: "Key-value object with options. Must be a JSON string or a state reference to a dictionary.",
				type: FieldType.KeyValue,
				default: JSON.stringify(defaultOptions, null, 2),
			},
			orientation: {
				name: "Orientation",
				type: FieldType.Text,
				options: {
					vertical: "Vertical",
					horizontal: "Horizontal",
				},
				default: "vertical",
				category: FieldCategory.Style,
				desc: "Specify how to lay out the options.",
			},
			cssClasses,
		},
		events: {
			"ss-options-change": {
				desc: "Sent when the selected options change.",
				stub: onChangeHandlerStub.trim(),
				bindable: true,
			},
		},
	},
};
</script>

<script setup lang="ts">
import injectionKeys from "../../injectionKeys";
import { useFormValueBroker } from "../../renderer/useFormValueBroker";

const fields = inject(injectionKeys.evaluatedFields);
const rootEl: Ref<HTMLElement> = ref(null);
const ss = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);
const flattenedInstancePath = inject(injectionKeys.flattenedInstancePath);

const { formValue, handleInput } = useFormValueBroker(ss, instancePath, rootEl);

function getCheckedKeys() {
	if (!rootEl.value) return;
	const checkboxEls = Array.from(
		rootEl.value.querySelectorAll(`input[type="checkbox"]`),
	) as HTMLInputElement[];
	const checkedValues = checkboxEls
		.map((checkboxEl) =>
			checkboxEl.checked ? checkboxEl.value : undefined,
		)
		.filter((el) => typeof el != "undefined");
	return checkedValues;
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
.CoreCheckboxInput {
	width: 100%;
}

.mainLabel:not(:empty) {
	margin-bottom: 12px;
}

.options {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.options.horizontal {
	flex-direction: row;
	flex-wrap: wrap;
}

.option {
	display: flex;
	align-items: center;
	color: var(--primaryTextColor);
	font-size: 0.75rem;
}

input {
	margin: 0 8px 0 0;
}

label {
	color: var(--primaryTextColor);
}
</style>
