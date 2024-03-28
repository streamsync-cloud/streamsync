<template>
	<div class="BuilderInsertionLabel">
		<slot></slot>
	</div>
</template>
<style scoped>
.BuilderInsertionLabel {
	display: flex;
	align-items: center;
	justify-content: center;
	overflow: hidden;
	white-space: nowrap;
	box-shadow: 0 0 8px -1px rgba(0, 0, 0, 0.6);
	position: absolute;
	border-radius: 18px;
	padding: 0 16px 0 16px;
	height: 36px;
	font-size: 0.75rem;
	color: var(--builderBackgroundColor);
	background: var(--builderIntenseSelectedColor);
}
</style>
