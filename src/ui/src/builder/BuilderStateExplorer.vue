<template>
	<div class="BuilderStateExplorer">
		<BuilderStateExplorerTreeBranch
			:root-accessors="[]"
		></BuilderStateExplorerTreeBranch>
	</div>
</template>

<script setup lang="ts">
import BuilderStateExplorerTreeBranch from "./BuilderStateExplorerTreeBranch.vue";
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderStateExplorer {
	max-height: 70vh;
	overflow-y: auto;
}
</style>
