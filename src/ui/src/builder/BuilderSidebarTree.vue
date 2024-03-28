<template>
	<div class="BuilderSidebarTree">
		<div v-if="!isSearchActive" class="sectionTitle">
			<i class="ri-node-tree ri-xl"></i>
			<h3>Component Tree</h3>
			<i
				class="ri-search-line ri-xl searchIcon"
				title="Search"
				@click="toggleSearch"
			></i>
		</div>
		<div v-if="isSearchActive" class="sectionTitle">
			<input
				ref="searchInput"
				v-model="searchQuery"
				type="text"
				placeholder="Search..."
			/>
			<i
				class="ri-arrow-left-s-line ri-xl searchIcon"
				:class="{ disabled: !matchAvailable }"
				:title="
					matchAvailable
						? `Go to match ${previousMatchIndex + 1} of ${matchingComponents.length}`
						: `Previous match`
				"
				@click="goToPreviousMatch"
			></i>
			<i
				class="ri-arrow-right-s-line ri-xl searchIcon"
				:class="{ disabled: !matchAvailable }"
				:title="
					matchAvailable
						? `Go to match ${nextMatchIndex + 1} of ${matchingComponents.length}`
						: `Next match`
				"
				@click="goToNextMatch"
			></i>
			<i
				class="ri-close-line ri-xl searchIcon"
				title="Close"
				@click="toggleSearch"
			></i>
		</div>
		<div ref="componentTree" class="components">
			<div
				v-for="component in rootComponents"
				:key="component.id"
				class="selector"
			>
				<BuilderTreeBranch
					:component-id="component.id"
					:matching-components="matchingComponents"
				></BuilderTreeBranch>
			</div>
		</div>
		<div class="addPage">
			<button @click="addPage">
				<i class="ri-add-line"></i>Add Page
			</button>
		</div>
	</div>
</template>

<script setup lang="ts">
import { inject, computed, nextTick, ref, Ref, ComputedRef } from "vue";
import { useComponentActions } from "./useComponentActions";
import BuilderTreeBranch from "./BuilderTreeBranch.vue";
import injectionKeys from "../injectionKeys";
import { Component } from "../streamsyncTypes";
import { watch } from "vue";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const { createAndInsertComponent, goToComponentParentPage } =
	useComponentActions(ss, ssbm);

const searchInput: Ref<HTMLInputElement> = ref(null);
const isSearchActive: Ref<boolean> = ref(false);
const searchQuery: Ref<string> = ref(null);
const matchIndex: Ref<number> = ref(-1);
const rootComponents = computed(() => {
	return ss.getComponents(null, { sortedByPosition: true });
});

async function toggleSearch() {
	isSearchActive.value = !isSearchActive.value;
	if (isSearchActive.value) {
		await nextTick();
		searchInput.value.focus();
	} else {
		searchQuery.value = null;
	}
}

function determineMatch(component: Component, query: string): boolean {
	if (component.id.toLocaleLowerCase().includes(query)) return true;
	if (component.type.toLocaleLowerCase().includes(query)) return true;
	const typeName = ss.getComponentDefinition(component.type)?.name;
	if (typeName.includes(query)) return true;
	const fields = [
		...Object.values(component.content ?? {}),
		...Object.values(component.handlers ?? {}),
		...Object.values(component.binding ?? {}),
	];
	for (let i = 0; i < fields.length; i++) {
		const fieldValue = fields[i]?.toString().toLocaleLowerCase();
		if (fieldValue?.includes(query)) return true;
	}
	return false;
}

async function selectMatch() {
	const component = matchingComponents.value?.[matchIndex.value];
	if (!component) return;
	goToComponentParentPage(component.id);
	await nextTick();
	ssbm.setSelection(component.id);
}

const previousMatchIndex = computed(() => {
	if (!matchAvailable.value) return -1;
	let i = matchIndex.value - 1;
	if (i < 0) {
		i = matchingComponents.value.length - 1;
	}
	return i;
});

const nextMatchIndex = computed(() => {
	if (!matchAvailable.value) return -1;
	let i = matchIndex.value + 1;
	if (i > matchingComponents.value.length - 1) {
		i = 0;
	}
	return i;
});

function goToPreviousMatch() {
	matchIndex.value = previousMatchIndex.value;
	selectMatch();
}

function goToNextMatch() {
	matchIndex.value = nextMatchIndex.value;
	selectMatch();
}

const matchingComponents: ComputedRef<Component[]> = computed(() => {
	if (!isSearchActive.value) return;
	if (!searchQuery.value) return;
	const query = searchQuery.value.toLocaleLowerCase();
	const components = ss.getComponents();
	const matching = components.filter((c) => determineMatch(c, query));
	return matching;
});

watch(matchingComponents, () => {
	matchIndex.value = -1;
});

const matchAvailable: ComputedRef<boolean> = computed(
	() => matchingComponents.value?.length > 0,
);

async function addPage() {
	const pageId = createAndInsertComponent("page", "root");
	ss.setActivePageId(pageId);
	await nextTick();
	ssbm.setSelection(pageId);
}
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSidebarTree {
	user-select: none;
	position: relative;
	display: flex;
	flex-direction: column;
}

.sectionTitle {
	background: var(--builderBackgroundColor);
	padding: 16px;
	top: 0;
	position: sticky;
}

.sectionTitle h3 {
	flex-grow: 1;
}

.sectionTitle .searchIcon {
	cursor: pointer;
}

.sectionTitle .searchIcon.disabled {
	color: var(--builderDisabledColor);
}

.sectionTitle input {
	outline: 0;
	border: 0;
	flex-grow: 1;
	width: 50%;
}

.components {
	padding: 0 12px 12px 12px;
}

.addPage {
	margin-top: auto;
	padding: 0 16px 16px 16px;
}
</style>
