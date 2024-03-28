<template>
	<div
		v-if="
			isBeingEdited || Object.entries(fields.tags.value ?? []).length > 0
		"
		ref="rootEl"
		class="CoreTags"
	>
		<template v-if="Object.entries(fields.tags.value ?? []).length > 0">
			<div
				v-for="(tagDesc, tagId) in fields.tags.value"
				:key="tagId"
				class="tag"
				:style="{ background: generateColor(tagId) }"
				@click="() => handleTagClick(tagId)"
			>
				{{ tagDesc }}
			</div>
		</template>
		<div v-else class="tag empty">
			<span>Empty Tags</span>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import { cssClasses, primaryTextColor } from "../../renderer/sharedStyleFields";

const clickHandlerStub = `
def handle_tag_click(state, payload):
	state["selected_tag_id"] = payload`;

const description = "A component to display coloured tag pills.";

export default {
	streamsync: {
		name: "Tags",
		description,
		category: "Content",
		fields: {
			tags: {
				name: "Tags",
				desc: "Key-value object with tags. Must be a JSON string or a state reference to a dictionary.",
				type: FieldType.KeyValue,
				default: "{}",
			},
			referenceColor: {
				name: "Reference",
				desc: "The colour to be used as reference for chroma and luminance, and as the starting point for hue rotation.",
				type: FieldType.Color,
				default: "#29cf00",
				category: FieldCategory.Style,
			},
			seed: {
				name: "Seed value",
				desc: "Choose a different value to reshuffle colours.",
				type: FieldType.Number,
				default: "1",
				category: FieldCategory.Style,
			},
			rotateHue: {
				name: "Rotate hue",
				desc: "If active, rotates the hue depending on the content of the string. If turned off, the reference colour is always used.",
				type: FieldType.Text,
				options: {
					yes: "yes",
					no: "no",
				},
				default: "yes",
				category: FieldCategory.Style,
			},
			primaryTextColor: {
				...primaryTextColor,
				default: "#ffffff",
			},
			cssClasses,
		},
		events: {
			"ss-tag-click": {
				desc: "Triggered when a tag is clicked.",
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
import chroma from "chroma-js";

const COLOR_STEPS = 18;
const rootEl: Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);
const componentId = inject(injectionKeys.componentId);
const ss = inject(injectionKeys.core);
const isBeingEdited = inject(injectionKeys.isBeingEdited);

const isClickable = computed(() => {
	const component = ss.getComponentById(componentId);
	return typeof component.handlers?.["ss-tag-click"] !== "undefined";
});

function generateColor(s: string) {
	if (fields.rotateHue.value == "no") {
		return fields.referenceColor.value;
	}
	const baseColor = chroma(fields.referenceColor.value);
	let genColor = baseColor.set(
		"hcl.h",
		`+${calculateColorStep(s) * (360 / COLOR_STEPS)}`,
	);
	return genColor.css();
}

function calculateColorStep(s: string) {
	let hash = (fields.seed.value * 52673) & 0xffffffff;
	for (let i = 0; i < s.length; i++) {
		hash = ((i + 1) * s.charCodeAt(i)) ^ (hash & 0xffffffff);
	}
	const step = Math.abs(hash) % COLOR_STEPS;
	return step;
}

function handleTagClick(tagId: string) {
	const event = new CustomEvent("ss-tag-click", {
		detail: {
			payload: tagId,
		},
	});
	rootEl.value.dispatchEvent(event);
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreTags {
	display: flex;
	gap: 8px;
	flex-wrap: wrap;
	align-items: center;
}

.tag {
	height: fit-content;
	padding: 4px 8px 4px 8px;
	border-radius: 16px;
	font-size: 0.65rem;
	color: var(--primaryTextColor);
	display: flex;
	align-items: center;
	gap: 4px;
	cursor: v-bind("isClickable ? 'pointer' : 'auto'");
}

.tag.empty {
	background-color: var(--separatorColor);
	color: var(--primaryTextColor);
}

.tag.empty span {
	opacity: 0.8;
}
</style>
