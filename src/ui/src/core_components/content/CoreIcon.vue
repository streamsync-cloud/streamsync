<docs lang="md">
    Streamsync uses the library RemixIcon to display icons. To include an icon, check remixicon.com, find the icon's id (such as \`arrow-up\`)
</docs>

<template>
	<div
		class="icon"
		v-tooltip="{
			content: fields.tooltip.value,
			placement: fields.tooltipLocation.value,
		}"
	>
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

/* This is used for removing the arrow on the tooltip */
<style>
.v-popper__arrow-container {
	display: none;
}
</style>
