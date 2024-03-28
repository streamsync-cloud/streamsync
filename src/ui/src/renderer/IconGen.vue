<template>
	<div class="IconGen">
		<svg
			v-if="iconKey == 'collapseArrow'"
			width="5"
			height="9"
			viewBox="0 0 5 9"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
		>
			<path d="M4 1L1 4.64L4 8" />
		</svg>
	</div>
</template>

<script setup lang="ts">
import { toRefs } from "vue";

const props = defineProps<{
	iconKey: "collapseArrow";
}>();
const { iconKey } = toRefs(props);
</script>

<style scoped>
path {
	color: currentColor;
}
</style>
