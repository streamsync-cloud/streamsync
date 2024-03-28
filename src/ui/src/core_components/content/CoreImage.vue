<docs lang="md">
Use your app's static folder to serve images directly. For example, \`static/my_image.png\`.

Alternatively, pass a Matplotlib figure via state.

\`state["my_fig"] = fig\` and then setting the _Image_ source to \`@{fig}\`

You can also use packed files or bytes:

\`state["img_b"] = ss.pack_bytes(img_bytes, "image/png")\`

\`state["img_f"] = ss.pack_file(img_file, "image/png")\`
</docs>

<template>
	<div ref="rootEl" class="CoreImage" :style="rootStyle" @click="handleClick">
		<img
			:src="fields.src.value"
			:alt="fields.caption.value"
			draggable="false"
			:style="imgStyle"
		/>
		<div
			v-if="fields.caption.value || fields.caption.value === 0"
			class="captionContainer"
		>
			{{ fields.caption.value }}
		</div>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import {
	cssClasses,
	secondaryTextColor,
} from "../../renderer/sharedStyleFields";
import { getClick } from "../../renderer/syntheticEvents";

const description = "A component to display images.";

const clickHandlerStub = `
def click_handler(state):

	# Increment counter when the image is clicked

	state["counter"] += 1`;

export default {
	streamsync: {
		name: "Image",
		description,
		category: "Content",
		fields: {
			src: {
				name: "Source",
				default:
					"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjMwIiBoZWlnaHQ9IjIzMCIgdmlld0JveD0iMCAwIDIzMCAyMzAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMzAiIGhlaWdodD0iMjMwIiBmaWxsPSIjREFEQURBIi8+CjxyZWN0IHg9Ijg2LjA0MzkiIHk9Ijc4IiB3aWR0aD0iNzEuMjkzNyIgaGVpZ2h0PSIzNC42NDY3IiByeD0iMTcuMzIzMyIgZmlsbD0id2hpdGUiIHN0cm9rZT0id2hpdGUiLz4KPHJlY3QgeD0iNzIuNSIgeT0iMTEzLjY5MyIgd2lkdGg9IjcwLjI5MzciIGhlaWdodD0iMzYuODA3MyIgcng9IjE3LjUiIGZpbGw9IndoaXRlIiBzdHJva2U9IndoaXRlIi8+Cjwvc3ZnPgo=",
				desc: "A valid URL. Alternatively, you can provide a state reference to a Matplotlib figure or a packed file.",
				type: FieldType.Text,
			},
			caption: {
				name: "Caption",
				init: "Image Caption",
				desc: "Leave blank to hide.",
				type: FieldType.Text,
			},
			maxWidth: {
				name: "Max width (px)",
				type: FieldType.Number,
				default: "-1",
				category: FieldCategory.Style,
			},
			maxHeight: {
				name: "Max height (px)",
				type: FieldType.Number,
				default: "-1",
				category: FieldCategory.Style,
			},
			secondaryTextColor,
			cssClasses,
		},
		events: {
			"ss-click": {
				desc: "Capture single clicks.",
				stub: clickHandlerStub.trim(),
			},
		},
		previewField: "caption",
	},
};
</script>

<script setup lang="ts">
import { Ref, computed, inject, ref } from "vue";
import injectionKeys from "../../injectionKeys";

const rootEl: Ref<HTMLElement> = ref(null);
const ss = inject(injectionKeys.core);
const fields = inject(injectionKeys.evaluatedFields);
const componentId = inject(injectionKeys.componentId);

const rootStyle = computed(() => {
	const component = ss.getComponentById(componentId);
	const isClickHandled =
		typeof component.handlers?.["ss-click"] !== "undefined";

	return {
		cursor: isClickHandled ? "pointer" : "unset",
	};
});

const imgStyle = computed(() => {
	const maxWidth = fields.maxWidth.value;
	const maxHeight = fields.maxHeight.value;
	return {
		"max-width": maxWidth !== -1 ? `${maxWidth}px` : undefined,
		"max-height": maxHeight !== -1 ? `${maxHeight}px` : undefined,
	};
});

function handleClick(ev: MouseEvent) {
	const ssEv = getClick(ev);
	rootEl.value.dispatchEvent(ssEv);
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreImage {
	width: fit-content;
}

img {
	max-width: 100%;
}

.CoreImage.selected img {
	opacity: 0.5;
	mix-blend-mode: multiply;
}
.captionContainer {
	color: var(--secondaryTextColor);
	text-align: center;
	font-size: 0.8rem;
	margin-top: 8px;
}
</style>
