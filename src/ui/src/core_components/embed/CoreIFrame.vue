<template>
	<div ref="rootEl" class="CoreIFrame">
		<div v-if="!fields.src.value" class="noURLProvided">
			<h2>No URL provided.</h2>
		</div>
		<iframe
			v-else
			:src="fields.src.value"
			draggable="false"
			@load="handleLoad"
		/>
		<div class="mask" />
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { cssClasses, separatorColor } from "../../renderer/sharedStyleFields";

const description = "A component to embed an external resource in an iframe.";

const loadHandlerStub = `
def load_handler(state):

	# Sets status message when resource is loaded

	state["status"] = "Page loaded"`;

export default {
	streamsync: {
		name: "IFrame",
		description,
		category: "Embed",
		fields: {
			src: {
				name: "Source",
				default: "",
				desc: "A valid URL",
				type: FieldType.Text,
			},
			separatorColor,
			cssClasses,
		},
		events: {
			"ss-load": {
				desc: "Fires when the resource has successfully loaded.",
				stub: loadHandlerStub.trim(),
			},
		},
	},
};
</script>

<script setup lang="ts">
import { Ref, inject, ref } from "vue";
import injectionKeys from "../../injectionKeys";

const rootEl: Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);

function handleLoad() {
	const event = new CustomEvent("ss-load");
	rootEl.value.dispatchEvent(event);
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreIFrame {
	position: relative;
	width: 100%;
	height: 80vh;
	border: 1px solid var(--separatorColor);
}

.noURLProvided {
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.CoreIFrame.beingEdited:not(.selected) iframe {
	pointer-events: none;
}

.CoreIFrame iframe {
	width: 100%;
	height: 100%;
	display: block;
	margin: auto;
	border: none;
	background: white;
}

.CoreIFrame .mask {
	pointer-events: none;
}

.CoreIFrame.beingEdited .mask {
	pointer-events: auto;
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0);
}

.CoreIFrame.beingEdited.selected .mask {
	pointer-events: none;
}
</style>
