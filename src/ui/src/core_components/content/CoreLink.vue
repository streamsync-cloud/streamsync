<template>
	<div class="CoreLink">
		<a
			:href="fields.url.value"
			:target="fields.target.value"
			:rel="fields.rel.value"
		>
			{{ displayText }}
		</a>
	</div>
</template>

<script lang="ts">
import { FieldType, Core } from "../../streamsyncTypes";
import { cssClasses, primaryTextColor } from "../../renderer/sharedStyleFields";
import injectionKeys from "../../injectionKeys";
export default {
	streamsync: {
		name: "Link",
		description: "A component to create a hyperlink.",
		category: "Content",
		fields: {
			url: {
				name: "URL",
				type: FieldType.Text,
				default: "https://streamsync.cloud",
				desc: "Specify a URL or choose a page. Keep in mind that you can only link to pages for which a key has been specified.",
				options: (ss: Core) => {
					return Object.fromEntries(
						ss
							.getComponents("root", { sortedByPosition: true })
							.map((page) => page.content.key)
							.filter((key) => Boolean(key))
							.map((key) => [`#${key}`, `Page with key: ${key}`]),
					);
				},
			},
			target: {
				name: "Target",
				type: FieldType.Text,
				options: {
					_self: "Self",
					_blank: "Blank",
					_parent: "Parent",
					_top: "Top",
				},
				desc: "Specifies where to open the linked document.",
				default: "_self",
			},
			rel: {
				name: "Rel",
				type: FieldType.Text,
				desc: "Specifies the relationship between the current document and the linked document.",
			},
			text: {
				name: "Text",
				default: "",
				type: FieldType.Text,
				desc: "The text to display in the link.",
			},
			primaryTextColor,
			cssClasses,
		},
	},
};
</script>

<script setup lang="ts">
import { inject, computed } from "vue";
const fields = inject(injectionKeys.evaluatedFields);

const displayText = computed(() => {
	return fields.text.value || fields.url.value;
});
</script>

<style scoped>
.CoreLink a {
	color: var(--primaryTextColor);
}
</style>
