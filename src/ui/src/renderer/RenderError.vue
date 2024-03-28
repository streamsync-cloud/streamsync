<template>
	<div class="RenderError">
		<div class="title">
			<h2>Error rendering {{ props.componentType }}</h2>
		</div>
		<div class="message">
			{{ props.message }}
		</div>
	</div>
</template>

<script setup lang="ts">
import { Component } from "../streamsyncTypes";

interface Props {
	componentType: Component["type"];
	message: string;
}

const props = defineProps<Props>();
</script>

<style scoped></style>
