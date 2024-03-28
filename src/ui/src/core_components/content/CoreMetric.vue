<template>
	<div class="CoreMetric" :style="rootStyle">
		<div v-if="fields.name.value" class="name">{{ fields.name.value }}</div>
		<div v-if="fields.description.value" class="description">
			{{ fields.description.value }}
		</div>
		<div class="value">{{ fields.metricValue.value }}</div>
		<div v-if="noteWithoutPrefix" class="note">{{ noteWithoutPrefix }}</div>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import {
	cssClasses,
	primaryTextColor,
	secondaryTextColor,
} from "../../renderer/sharedStyleFields";

const description =
	"A component that prominently displays a metric value and associated information.";

export default {
	streamsync: {
		name: "Metric",
		description,
		category: "Content",
		fields: {
			name: {
				name: "Name",
				default: "Metric",
				type: FieldType.Text,
			},
			metricValue: {
				name: "Value",
				default: "0",
				type: FieldType.Text,
				desc: "The main value to be displayed. It's not limited to numbers.",
			},
			description: {
				name: "Description",
				type: FieldType.Text,
			},
			note: {
				name: "Note",
				init: "+Pass",
				type: FieldType.Text,
				desc: "Prefix with '+' for a positive message, with '-' for a negative message.",
			},
			primaryTextColor,
			secondaryTextColor,
			positiveColor: {
				name: "Positive",
				default: "#00B800",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			neutralColor: {
				name: "Neutral",
				default: "var(--secondaryTextColor)",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			negativeColor: {
				name: "Negative",
				default: "#FB0000",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			cssClasses,
		},
		previewField: "name",
	},
};
</script>
<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "../../injectionKeys";
const fields = inject(injectionKeys.evaluatedFields);

const sentiment = computed(() => {
	const note: string = fields.note.value;
	if (!note) return "neutral";
	const firstChar = note.charAt(0);
	if (firstChar == "+") {
		return "positive";
	} else if (firstChar == "-") {
		return "negative";
	}
	return "neutral";
});

const noteWithoutPrefix = computed(() => {
	const note: string = fields.note.value;
	if (!note) return;
	const firstChar = note.charAt(0);
	if (firstChar == "+" || firstChar == "-") {
		return note.substring(1);
	}
	return note;
});

const rootStyle = computed(() => {
	const sentimentColors = {
		positive: fields.positiveColor.value,
		neutral: fields.neutralColor.value,
		negative: fields.negativeColor.value,
	};
	return {
		"--messageActiveSentimentColor": sentimentColors[sentiment.value],
	};
});
</script>
<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreMetric {
	color: var(--primaryTextColor);
	border-left: 4px solid transparent;
	padding-left: 16px;
	display: flex;
	flex-direction: column;
	gap: 8px;
	border-color: var(--messageActiveSentimentColor);
}

.name {
	font-size: 0.9rem;
}

.description {
	font-size: 0.75rem;
	color: var(--secondaryTextColor);
}

.value {
	overflow: hidden;
	text-overflow: ellipsis;
	font-size: 1.6rem;
}

.note {
	font-size: 0.9rem;
	color: var(--messageActiveSentimentColor);
	filter: brightness(0.9);
}
</style>
