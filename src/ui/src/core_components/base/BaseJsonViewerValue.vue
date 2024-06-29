<template>
	<span class="JsonViewerValue">{{ dataFormatted }}</span>
</template>

<script setup lang="ts">
import { PropType, computed } from "vue";
import type { JsonValue } from "./BaseJsonViewer.vue";

const props = defineProps({
	data: { type: Object as PropType<JsonValue>, required: true },
});

const dataFormatted = computed(() => JSON.stringify(props.data));
</script>

<style scoped>
.JsonViewerValue {
	font-family: monospace;
	color: var(--secondaryTextColor);
}
</style>
