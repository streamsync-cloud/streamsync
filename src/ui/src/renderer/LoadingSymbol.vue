<template>
	<div class="LoadingSymbol">
		<div></div>
	</div>
</template>

<script setup lang="ts"></script>

<style scoped>
@keyframes spin {
	0% {
		transform: rotate(0);
	}
	100% {
		transform: rotate(359deg);
	}
}

.LoadingSymbol {
	display: block;
	border-radius: 50%;
	height: 24px;
	width: 24px;
	background: var(--primaryTextColor);
	background: linear-gradient(90deg, #f0f0f0 1%, currentColor 50%);
	animation: spin 1s linear infinite;
	-webkit-mask-image: radial-gradient(12px, #0000 80%, #000);
	mask-image: radial-gradient(12px, #0000 80%, #000);
}
</style>
