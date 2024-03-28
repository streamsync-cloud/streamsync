<template>
	<div class="BuilderInsertionOverlay">
		<div class="overlay"></div>
		<div class="progressBar">
			<div class="elapsed" :style="elapsedAnimationStyle"></div>
		</div>
	</div>
</template>
<script setup lang="ts">
import { computed } from "vue";
import { CANDIDATE_CONFIRMATION_DELAY_MS } from "./builderManager";

const elapsedAnimationStyle = computed(() => ({
	"animation-duration": `${CANDIDATE_CONFIRMATION_DELAY_MS}ms`,
}));
</script>
<style scoped>
.BuilderInsertionOverlay {
	min-width: 100%;
	min-height: 100%;
	pointer-events: none;
	position: relative;
	display: flex;
	justify-content: start;
}

.overlay {
	width: 100%;
	height: 100%;
	position: absolute;
	opacity: 0.8;
	top: 0;
	left: 0;
	animation: 0.2s ease-in appear forwards;
}

.progressBar {
	position: absolute;
	top: 0;
	left: 0;
	height: 4px;
	width: 100%;
	background: var(--builderSeparatorColor);
}

.progressBar .elapsed {
	height: 4px;
	background: var(--builderIntenseSelectedColor);
	animation: linear elapse forwards;
}

@keyframes appear {
	from {
		background-color: transparent;
	}
	to {
		background-color: var(--builderSelectedColor);
	}
}

@keyframes elapse {
	from {
		width: 0;
	}
	to {
		width: 100%;
	}
}
</style>
