<template>
	<div ref="rootEl" class="CoreSwitchInput">
		<div
			class="switch"
			:class="{ on: toggleValue }"
			tabindex="0"
			role="switch"
			:aria-checked="toggleValue"
			@click="handleToggle"
			@keydown.enter.space="handleToggle"
		>
			<div class="toggle"></div>
		</div>
		<label @click="handleToggle">
			{{ fields.label.value }}
		</label>
	</div>
</template>

<script lang="ts">
import { inject, Ref } from "vue";
import { ref } from "vue";
import { FieldType } from "../../streamsyncTypes";
import {
	accentColor,
	primaryTextColor,
	separatorColor,
	cssClasses,
} from "../../renderer/sharedStyleFields";

const description = "A user input component with a simple on/off status.";

const onToggleHandlerStub = `
def handle_toggle(state, payload):

	# The payload will be a bool 

	state["its_on"] = payload`;

export default {
	streamsync: {
		name: "Switch Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			accentColor,
			primaryTextColor,
			separatorColor,
			cssClasses,
		},
		events: {
			"ss-toggle": {
				desc: "Sent when the switch is toggled.",
				stub: onToggleHandlerStub.trim(),
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
const { handleInput } = useFormValueBroker(ss, instancePath, rootEl);
const toggleValue = ref(false);

function handleToggle() {
	toggleValue.value = !toggleValue.value;
	handleInput(toggleValue.value, "ss-toggle");
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
.CoreSwitchInput {
	display: flex;
	gap: 8px;
	align-items: center;
}

.switch {
	background: var(--separatorColor);
	width: 32px;
	height: 16px;
	padding: 1px;
	border-radius: 8px;
	cursor: pointer;
	box-shadow: 0 0 2px 0px rgba(0, 0, 0, 0.2) inset;
	overflow: hidden;
}

.switch:focus-visible {
	outline: 1px solid var(--primaryTextColor);
}

.switch.on {
	background: var(--accentColor);
}

.toggle {
	width: 14px;
	height: 14px;
	background: var(--containerBackgroundColor);
	border-radius: 8px;
	transition: 0.2s margin ease-in-out;
}

.switch.on .toggle {
	margin-left: 16px;
}

label {
	cursor: pointer;
}
</style>
