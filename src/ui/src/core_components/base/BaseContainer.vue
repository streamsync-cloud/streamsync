<template>
	<div
		class="BaseContainer"
		:style="rootStyle"
		:class="{ horizontal: props.isHorizontal }"
		data-streamsync-container
	>
		<slot></slot>
	</div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
	contentHAlign: string;
	contentVAlign?: string;
	contentPadding: string;
	isHorizontal?: boolean;
}>();

const rootStyle = computed(() => {
	const baseStyle = {
		padding: props.contentPadding,
	};

	if (props.isHorizontal) {
		return {
			...baseStyle,
			justifyContent: props.contentHAlign,
			alignItems: props.contentVAlign,
		};
	}

	return {
		...baseStyle,
		alignItems: props.contentHAlign,
		justifyContent: props.contentVAlign,
	};
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.BaseContainer {
	display: flex;
	width: 100%;
}
</style>
