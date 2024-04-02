<template>
	<div
		ref="rootEl"
		class="CoreText"
		:style="rootStyle"
		@click="handleClick"
		v-tooltip="{
			content: fields.tooltip.value,
			placement: fields.tooltipLocation.value,
		}"
	>
		<BaseMarkdown
			v-if="fields.useMarkdown.value == 'yes'"
			:raw-text="fields.text.value"
			:style="contentStyle"
		>
		</BaseMarkdown>
		<div v-else class="plainText" :style="contentStyle">
			{{ fields.text.value }}
		</div>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldControl, FieldType } from "../../streamsyncTypes";
import { cssClasses, primaryTextColor } from "../../renderer/sharedStyleFields";
import { getClick } from "../../renderer/syntheticEvents";
import BaseMarkdown from "../base/BaseMarkdown.vue";

const clickHandlerStub = `
def click_handler(state):

	# Increment counter when the text is clicked

	state["counter"] += 1`;

const description =
	"A component to display plain text or formatted text using Markdown syntax.";

export default {
	streamsync: {
		name: "Text",
		description,
		category: "Content",
		fields: {
			text: {
				name: "Text",
				default: "(No text)",
				init: "Text",
				type: FieldType.Text,
				control: FieldControl.Textarea,
			},
			useMarkdown: {
				name: "Use Markdown",
				desc: "The Markdown output will be sanitised; unsafe elements will be removed.",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			tooltip: {
				name: "Tooltip text",
				type: FieldType.Text,
			},
			tooltipLocation: {
				name: "Tooltip location",
				type: FieldType.Text,
				default: "top",
				options: {
					"top-start": "top-start",
					top: "top",
					"top-end": "top-end",
					"right-start": "right-start",
					right: "right",
					"right-end": "right-end",
					"bottom-end": "bottom-end",
					bottom: "bottom",
					"bottom-start": "bottom-start",
					"left-end": "left-end",
					left: "left",
					"left-start": "left-start",
				},
			},
			alignment: {
				name: "Alignment",
				default: "left",
				type: FieldType.Text,
				options: {
					left: "Left",
					center: "Center",
					right: "Right",
				},
				category: FieldCategory.Style,
			},
			primaryTextColor,
			cssClasses,
		},
		events: {
			"ss-click": {
				desc: "Capture single clicks.",
				stub: clickHandlerStub.trim(),
			},
		},
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { Ref, computed, inject, ref } from "vue";
import injectionKeys from "../../injectionKeys";

const rootEl: Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);
const componentId = inject(injectionKeys.componentId);
const ss = inject(injectionKeys.core);

const rootStyle = computed(() => {
	const component = ss.getComponentById(componentId);
	const isClickHandled = typeof component.handlers?.["click"] !== "undefined";

	return {
		cursor: isClickHandled ? "pointer" : "unset",
	};
});

const contentStyle = computed(() => {
	return {
		"text-align": fields.alignment.value,
	};
});

function handleClick(ev: MouseEvent) {
	const ssEv = getClick(ev);
	rootEl.value.dispatchEvent(ssEv);
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreText {
	color: var(--primaryTextColor);
	line-height: 1.5;
	white-space: pre-wrap;
	max-width: 100%;
	overflow: hidden;
}

.CoreText ol,
.CoreText ul {
	white-space: normal;
}

.CoreText img {
	width: 100%;
}
</style>

/* This is used for removing the arrow on the tooltip */
<style>
.v-popper__arrow-container {
	display: none;
}
</style>
