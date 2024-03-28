<template>
	<div
		v-if="isMarkedLoaded"
		v-dompurify-html="marked.parse(props.rawText).trim()"
		class="BaseMarkdown markdown"
	></div>
</template>

<script setup lang="ts">
import { onBeforeMount, ref } from "vue";

let marked: typeof import("marked");
const isMarkedLoaded = ref(false);

const props = defineProps<{
	rawText: string;
}>();

onBeforeMount(async () => {
	marked = await import("marked");
	isMarkedLoaded.value = true;
});
</script>

<style scoped>
.markdown:deep() h1,
.markdown:deep() h2,
.markdown:deep() h3,
.markdown:deep() h4 {
	font-weight: 300;
	margin: 0;
	color: var(--primaryTextColor);
}

.markdown:deep() h1 {
	font-size: 1.3rem;
}

.markdown:deep() h2 {
	font-size: 1rem;
}

.markdown:deep() h3 {
	font-size: 0.9rem;
}

.markdown:deep() h4 {
	text-transform: uppercase;
	font-weight: bold;
	font-size: 0.65rem;
	letter-spacing: 0.2ch;
}

.markdown:deep() ul,
.markdown:deep() ol {
	padding: 0;
	padding-inline-start: 0;
	margin-block-start: 0;
}

.markdown:deep() li {
	margin: 0 0 0 32px;
}

.markdown:deep() hr {
	border: none;
	border-top: 1px solid var(--separatorColor);
}

.markdown:deep() pre {
	background-color: var(--separatorColor);
	font-family: monospace;
	padding: 8px;
}

.markdown:deep() code {
	background-color: var(--separatorColor);
	font-family: monospace;
	padding: 2px;
}

.markdown:deep() pre > code {
	background-color: unset;
}

.markdown:deep() table {
	border-collapse: collapse;
}

.markdown:deep() th {
	padding: 8px;
	background: var(--separatorColor);
	border: 1px solid var(--separatorColor);
}

.markdown:deep() td {
	padding: 8px;
	border: 1px solid var(--separatorColor);
}
</style>
