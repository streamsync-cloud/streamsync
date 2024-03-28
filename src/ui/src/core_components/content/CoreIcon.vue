<docs lang="md">
    Streamsync uses the library RemixIcon to display icons. To include an icon, check remixicon.com, find the icon's id (such as \`arrow-up\`)
</docs>

<template>
	<div class="icon">
		<i
			v-if="fields.icon.value"
			:class="[`ri-${fields.icon.value}-line`, `ri-${fields.icon.value}`]"
			:style="{
				fontSize: `${fields.size.value}px`,
				color: fields.color.value,
			}"
		></i>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

export default {
	streamsync: {
		name: "Icon",
		description: "A component to display an icon",
		category: "Content",
		fields: {
			icon: {
				name: "Icon",
				type: FieldType.Text,
				desc: `A RemixIcon id, such as "arrow-up".`,
				category: FieldCategory.Style,
				default: "square-line",
			},
			size: {
				name: "Icon size",
				type: FieldType.Number,
				desc: `Icon size in px`,
				category: FieldCategory.Style,
				default: 14,
			},
			color: {
				name: "Icon color",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			cssClasses,
		},
		previewField: "icon",
	},
};
</script>

<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "../../injectionKeys";

const fields = inject(injectionKeys.evaluatedFields);
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.icon {
	display: flex;
	align-items: center;
}
</style>
