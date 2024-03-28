<template>
	<div class="BuilderSwitcher">
		<div :class="{ active: activeId == 'ui' }" @click="selectOption('ui')">
			<i class="ri-brush-line"></i>
			User Interface
		</div>
		<div
			:class="{ active: activeId == 'code' }"
			@click="selectOption('code')"
		>
			<i class="ri-code-line"></i>
			Code
			<span v-show="logEntryCount > 0" class="countLabel">{{
				logEntryCount
			}}</span>
		</div>
		<div
			:class="{ active: activeId == 'preview' }"
			@click="selectOption('preview')"
		>
			<i class="ri-pages-line"></i>
			Preview
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, Ref, ref } from "vue";
import injectionKeys from "../injectionKeys";
const ssbm = inject(injectionKeys.builderManager);

let selectedId: Ref<string> = ref(null);

const selectOption = (optionId: "ui" | "code" | "preview") => {
	selectedId.value = optionId;
	ssbm.setMode(optionId);
	if (ssbm.getMode() != "preview") return;
	ssbm.setSelection(null);
};

const activeId = computed(() => {
	if (selectedId.value) return selectedId.value;
	const first = "ui";
	return first;
});

const logEntryCount = computed(() => {
	return ssbm.getLogEntryCount();
});
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSwitcher {
	background: var(--builderHeaderBackgroundHoleColor);
	color: white;
	font-size: 0.7rem;
	display: flex;
	gap: 0px;
	padding: 4px;
	border-radius: 4px;
	overflow: hidden;
}

.BuilderSwitcher div {
	padding: 4px 16px 4px 16px;
	height: 32px;
	cursor: pointer;
	display: flex;
	align-items: center;
}

.BuilderSwitcher div i {
	margin-right: 8px;
}

.BuilderSwitcher div.active {
	background: var(--builderHeaderBackgroundColor);
	border-radius: 4px;
}
</style>
