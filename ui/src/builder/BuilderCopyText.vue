<template>
	<span class="tooltip">
		<span class="tooltiptext">{{ copied }}</span>
		<span class="copyText" @click="copyText">
			<slot></slot>
		</span>
	</span>
</template>

<script setup lang="ts">
import { ref } from "vue";
const copied = ref("Copy to clipboard");

const copyText = (e) => {
	const copyText = e.target.textContent;
	navigator.clipboard.writeText(copyText);
	copied.value = "Copied!";
	setTimeout(() => {
		copied.value = "Copy to clipboard";
	}, 1000);
};
</script>

<style scoped>
.tooltip {
	position: relative;
	display: inline-block;
}

.tooltip .tooltiptext {
	visibility: hidden;
	background-color: var(--builderActionOngoingColor);
	color: var(--builderBackgroundColor);
	text-align: center;
	border-radius: 16px;
	padding: 4px 12px;
	position: absolute;
	z-index: 1;
	bottom: 150%;
	left: 50%;
	opacity: 0;
	white-space: nowrap;
	transition: opacity 0.3s;
	transform: translateX(-50%);
}

.tooltip .tooltiptext::after {
	content: "";
	position: absolute;
	top: 100%;
	left: 50%;
	margin-left: -5px;
	border-width: 5px;
	border-style: solid;
	border-color: var(--builderActionOngoingColor) transparent transparent
		transparent;
}

.tooltip:hover .tooltiptext {
	visibility: visible;
	opacity: 1;
}
.copyText {
	cursor: pointer;
}

.copyText:hover {
	text-decoration: underline;
}
</style>
