<template>
	<span>{{ text }}</span>
</template>

<script setup lang="ts">
import { PropType, computed } from "vue";
import {
	getJSONLength,
	isJSONArray,
	isJSONObject,
} from "./BaseJsonViewer.utils";
import type { JsonData } from "./BaseJsonViewer.vue";

const props = defineProps({
	data: {
		type: Object as PropType<JsonData>,
		required: true,
	},
});

const printObject = (length: number) => `Object{${length}}`;
const printArray = (length: number) => `Array[${length}]`;

const text = computed(() => {
	const count = getJSONLength(props.data);

	if (count === 0) return printObject(0);
	if (isJSONArray(props.data)) return printArray(count);
	if (isJSONObject(props.data)) return printObject(count);
	return printObject(0);
});
</script>

<style scoped>
span {
	color: var(--secondaryTextColor);
	font-family: monospace;
	font-size: 12px;
}
</style>
