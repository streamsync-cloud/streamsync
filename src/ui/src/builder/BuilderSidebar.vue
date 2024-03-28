<template>
	<div class="BuilderSidebar">
		<BuilderSidebarToolbar class="toolbar"></BuilderSidebarToolbar>
		<BuilderSidebarTree class="tree"></BuilderSidebarTree>
	</div>
</template>

<script setup lang="ts">
import BuilderSidebarToolbar from "./BuilderSidebarToolbar.vue";
import BuilderSidebarTree from "./BuilderSidebarTree.vue";
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSidebar {
	display: flex;
	flex-direction: column;
	height: 100%;
}

.toolbar {
	position: relative;
	height: 50%;
	display: flex;
	flex-direction: column;
	overflow-y: scroll;
}

.tree {
	height: 50%;
	overflow-y: auto;
	border-top: 1px solid var(--builderSeparatorColor);
}
</style>
