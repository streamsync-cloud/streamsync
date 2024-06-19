<template>
	<details
		class="collapsible"
		:open="open"
		:disabled="disabled"
		@toggle="onToggle"
	>
		<summary><slot name="title" /></summary>
		<div class="content">
			<slot name="content" />
		</div>
	</details>
</template>

<script setup lang="ts">
defineProps({
	open: { type: Boolean, required: false },
	disabled: { type: Boolean, required: false },
});

const emit = defineEmits({
	toggle: (open: boolean) => typeof open === "boolean",
});

function onToggle(event) {
	emit("toggle", event.newState === "open");
}
</script>

<style scoped>
/* customize the triangle and animate it */

details {
	box-sizing: border-box;
}

details summary::-webkit-details-marker {
	display: none;
}

details[open] > summary:before {
	transform: rotate(90deg);
}

summary {
	outline: none;
	display: flex;
	padding-left: 16px;
	position: relative;
	cursor: pointer;
}

summary:before {
	content: "";
	border-width: 6px;
	border-style: solid;
	border-color: transparent transparent transparent var(--accentColor);
	position: absolute;
	left: 4px;
	top: 2px;

	transform: rotate(0);
	transform-origin: 3px 50%;
	transition: 0.3s transform ease;
}

summary:focus-visible:before {
	border-color: transparent transparent transparent var(--primaryTextColor);
}

@media (prefers-reduced-motion) {
	summary:before {
		transition: unset;
	}
}

/* small animation on the content */

details[open] summary ~ .content {
	animation: sweep 0.2s ease-in-out;
}

@media (prefers-reduced-motion) {
	details[open] summary ~ .content {
		animation: unset;
	}
}

@keyframes sweep {
	0% {
		opacity: 0;
		margin-top: -12px;
	}
	100% {
		opacity: 1;
		margin-top: 0;
	}
}
</style>
