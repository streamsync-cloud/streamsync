<template>
	<BaseCollapsible
		:open="open"
		:disabled="disabled"
		@toggle="$emit('toggle', $event)"
	>
		<template #title>
			<div class="BaseJsonViewerCollapsible__title">
				<span v-if="title">{{ title }}</span>
				<BaseJsonViewerChildrenCounter v-if="data" :data="data" />
			</div>
		</template>
		<template #content>
			<div class="BaseJsonViewerCollapsible__content">
				<slot />
			</div>
		</template>
	</BaseCollapsible>
</template>

<script setup lang="ts">
import type { PropType } from "vue";
import BaseCollapsible from "./BaseCollapsible.vue";
import type { JsonData } from "./BaseJsonViewer.vue";
import BaseJsonViewerChildrenCounter from "./BaseJsonViewerChildrenCounter.vue";

defineProps({
	open: { type: Boolean, required: false },
	disabled: { type: Boolean, required: false },
	title: { type: String, required: false, default: undefined },
	data: {
		type: [Object, Array] as PropType<JsonData>,
		required: false,
		default: undefined,
	},
});

defineEmits({
	toggle: (open: boolean) => typeof open === "boolean",
});
</script>

<style scoped>
.BaseJsonViewerCollapsible__title {
	font-family: monospace;
	font-size: 12px;
	display: flex;
	gap: 8px;
}

.BaseJsonViewerCollapsible__content {
	margin-left: 7px;
	padding-left: var(--jsonViewerIndentationSpacing, 8px);
	padding-top: 4px;
	padding-bottom: 4px;
	border-left: 1px solid var(--separatorColor);
}
</style>
