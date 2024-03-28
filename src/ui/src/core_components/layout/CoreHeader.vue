<template>
	<div class="CoreHeader">
		<div class="rectangle">
			<h1>{{ fields.text.value }}</h1>
		</div>
		<div class="container horizontal" data-streamsync-container>
			<slot></slot>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import {
	accentColor,
	cssClasses,
	emptinessColor,
} from "../../renderer/sharedStyleFields";

const description =
	"A container component that typically contains the main navigation elements.";

export default {
	streamsync: {
		name: "Header",
		description,
		category: "Layout",
		allowedChildrenTypes: ["*"],
		fields: {
			text: {
				name: "Text",
				init: "Header Text",
				default: "(No text)",
				type: FieldType.Text,
			},
			accentColor,
			emptinessColor,
			cssClasses,
		},
		previewField: "text",
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

.CoreHeader {
	display: flex;
	flex-wrap: wrap;
	gap: 16px;
	max-width: 100%;
}

.rectangle {
	background: var(--accentColor);
	padding: 16px;
	width: fit-content;
	flex: 0 0 auto;
	display: flex;
	align-items: center;
}

h1 {
	color: var(--emptinessColor);
}

.container {
	max-width: 100%;
	flex: 2 0 auto;
	align-items: center;
	justify-content: right;
	flex-wrap: wrap;
}
</style>
