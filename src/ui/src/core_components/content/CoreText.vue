<template>
	<div
		v-if="isDisplayed"
		ref="rootEl"
		class="CoreText"
		:style="rootStyle"
		@click="handleClick"
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
import { cssClasses, primaryTextColor } from "../../renderer/sharedStyleFields";
import { getClick } from "../../renderer/syntheticEvents";
import { FieldCategory, FieldControl, FieldType } from "../../writerTypes";
import BaseMarkdown from "../base/BaseMarkdown.vue";

const clickHandlerStub = `
def click_handler(state):

	# Increment counter when the text is clicked

	state["counter"] += 1`;

const description =
	"A component to display plain text or formatted text using Markdown syntax.";

const emptyText = "(No text)";

export default {
	writer: {
		name: "Text",
		description,
		category: "Content",
		fields: {
			text: {
				name: "Text",
				default: emptyText,
				init: "Text",
				desc: "Add text directly, or reference state elements with @{my_text}.",
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
			"wf-click": {
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
const isBeingEdited = inject(injectionKeys.isBeingEdited);
const wf = inject(injectionKeys.core);

const isDisplayed = computed(
	() => isBeingEdited.value || fields.text.value !== emptyText,
);

const rootStyle = computed(() => {
	const component = wf.getComponentById(componentId);
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
	line-height: 140%;
	white-space: pre-wrap;
	max-width: 100%;
	overflow: hidden;
	font-size: 0.875rem;
	font-weight: 400;
}

.CoreText ol,
.CoreText ul {
	white-space: normal;
}

.CoreText img {
	width: 100%;
}
</style>
