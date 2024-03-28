<template>
	<div class="BuilderTreeBranch">
		<div
			ref="rootEl"
			class="main"
			:class="{
				selected: isSelected,
				childless: childless,
				matching: isMatching,
			}"
			:title="summaryText"
			:data-branch-component-id="componentId"
			tabindex="0"
			:draggable="isDraggingAllowed(componentId)"
			@click="selfSelectComponent"
			@keydown.enter="selfSelectComponent"
			@dragover="handleDragOver"
			@dragstart="handleDragStart"
			@dragend="handleDragEnd"
			@drop="handleDrop"
		>
			<div
				v-if="!childless"
				class="toggleChildren"
				@click="toggleChildrenVisible"
			>
				<i
					v-if="childrenVisible"
					class="ri-arrow-drop-up-line ri-lg"
				></i>
				<i
					v-if="!childrenVisible"
					class="ri-arrow-drop-down-line ri-lg"
				></i>
			</div>
			<span class="type">{{ name }}</span>
			<template v-if="Object.keys(component.handlers ?? {}).length > 0">
				&nbsp;&middot;&nbsp;<i class="ri-flashlight-line ri-lg"></i>
			</template>
			<template v-if="!isComponentVisible(component.id)">
				&nbsp;&middot;&nbsp;<i class="ri-eye-off-line ri-lg"></i>
			</template>
			<template v-if="component.isCodeManaged">
				&nbsp;&middot;&nbsp;<i class="ri-terminal-box-line ri-lg"></i>
			</template>

			<span v-if="previewText" class="preview">
				&nbsp;&middot;&nbsp;{{ previewText }}</span
			>
		</div>
		<div v-if="childrenVisible && !childless" class="children">
			<div
				v-for="childComponent in childrenComponents.filter(
					(c) => !c.isCodeManaged,
				)"
				:key="childComponent.id"
				class="child"
			>
				<BuilderTreeBranch
					:component-id="childComponent.id"
					:matching-components="matchingComponents"
				></BuilderTreeBranch>
			</div>
			<div
				v-for="childComponent in childrenComponents.filter(
					(c) => c.isCodeManaged,
				)"
				:key="childComponent.id"
				class="child"
			>
				<BuilderTreeBranch
					:component-id="childComponent.id"
					:matching-components="matchingComponents"
				></BuilderTreeBranch>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { useComponentActions } from "./useComponentActions";
import { useDragDropComponent } from "./useDragDropComponent";
import { computed, inject, nextTick, Ref, ref, toRefs, watch } from "vue";
import { Component } from "../streamsyncTypes";
import injectionKeys from "../injectionKeys";
import { onMounted } from "vue";
import { useEvaluator } from "../renderer/useEvaluator";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const {
	createAndInsertComponent,
	moveComponent,
	goToComponentParentPage,
	isDraggingAllowed,
} = useComponentActions(ss, ssbm);
const { getComponentInfoFromDrag, removeInsertionCandidacy, isParentSuitable } =
	useDragDropComponent(ss);
const { isComponentVisible } = useEvaluator(ss);

interface Props {
	componentId: Component["id"];
	matchingComponents?: Component[];
}

const props = defineProps<Props>();
const { componentId, matchingComponents } = toRefs(props);
const component = computed(() => {
	return ss.getComponentById(componentId.value);
});

const isSelectedBySelf = ref(false);
const rootEl: Ref<HTMLElement> = ref(null);

const componentDefinition = computed(() =>
	ss.getComponentDefinition(component.value.type),
);

const name = computed(() => {
	const name =
		componentDefinition.value?.name ?? `Unknown (${component.value.type})`;
	if (component.value.type !== "html") return name;
	const element = component.value.content?.element;
	if (element) return `${element}`;
	return name;
});

const childless = computed(() => {
	if (childrenComponents.value.length == 0) return true;
	if (!componentDefinition.value) return true; // Hide children of unknown component types
	return false;
});

const isMatching = computed(() => {
	if (matchingComponents.value?.some((c) => c.id == componentId.value))
		return true;
	return false;
});

const previewText = computed(() => {
	const key = componentDefinition.value?.previewField;
	if (!key) return;
	const component = ss.getComponentById(componentId.value);
	const text = component.content?.[key];

	let shortenedText: string;
	const MAX_PREVIEW_TEXT_LENGTH = 70;
	if (text?.length > MAX_PREVIEW_TEXT_LENGTH) {
		shortenedText = text.substring(0, MAX_PREVIEW_TEXT_LENGTH) + "...";
	} else {
		shortenedText = text;
	}

	return shortenedText;
});

const summaryText = computed(() => {
	let text = name.value;
	if (previewText.value) {
		text += ` · ${previewText.value}`;
	}
	text += ` · Position: ${component.value.position}`;
	return text;
});

const childrenComponents = computed(() => {
	return ss.getComponents(componentId.value, { sortedByPosition: true });
});

const childrenVisible = ref(true);

const toggleChildrenVisible = () => {
	childrenVisible.value = !childrenVisible.value;
};

async function selfSelectComponent() {
	goToComponentParentPage(componentId.value);
	await nextTick();
	ssbm.setSelection(componentId.value);
	isSelectedBySelf.value = true;
}

const selectedId = computed(() => ssbm.getSelectedId());
const isSelected = computed(() => {
	return selectedId.value == component.value?.id;
});

watch(selectedId, (newSelectedId) => {
	if (!newSelectedId) return;
	const selected = ss.getComponentById(newSelectedId);
	let parentId = selected.parentId;
	while (parentId) {
		if (parentId === componentId.value) {
			childrenVisible.value = true;
			break;
		}
		parentId = ss.getComponentById(parentId)?.parentId;
	}
});

watch(isSelected, async (newIsSelected) => {
	if (!newIsSelected) return;
	if (!isSelectedBySelf.value) {
		scrollTreeToShowRootElement();
		return;
	}
	isSelectedBySelf.value = false;
});

const scrollTreeToShowRootElement = () => {
	if (!rootEl.value) return;
	const treeEl = rootEl.value.closest(".BuilderSidebarTree");
	const treeHeight = treeEl.clientHeight;
	const rootElHeight = rootEl.value.clientHeight;
	const scrollTop =
		rootEl.value.offsetTop - (treeHeight / 2 - rootElHeight / 2);

	treeEl.scrollTo({ top: scrollTop, left: 0, behavior: "smooth" });
};

const handleDragStart = (ev: DragEvent) => {
	ssbm.setSelection(null);
	ev.dataTransfer.setData(
		`application/json;streamsync=${component.value.type},${component.value.id}`,
		"{}",
	);
};

const handleDragEnd = (ev: DragEvent) => {
	removeInsertionCandidacy(ev);
};

const handleDragOver = (ev: DragEvent) => {
	const dragInfo = getComponentInfoFromDrag(ev);
	if (!dragInfo) return;
	const { draggedType, draggedId } = dragInfo;
	if (!isParentSuitable(componentId.value, draggedId, draggedType)) return;
	ev.preventDefault();
};

const handleDrop = (ev: DragEvent) => {
	const dragInfo = getComponentInfoFromDrag(ev);
	if (!dragInfo) return;
	const { draggedType, draggedId } = dragInfo;

	if (!draggedId) {
		createAndInsertComponent(draggedType, component.value.id);
	} else {
		moveComponent(draggedId, component.value.id);
	}

	removeInsertionCandidacy(ev);
};

onMounted(() => {
	if (!isSelected.value) return;
	scrollTreeToShowRootElement();
});
</script>

<style scoped>
@import "./sharedStyles.css";

.main {
	padding: 4px 8px 4px 8px;
	min-height: 32px;
	font-size: 0.7rem;
	border-radius: 4px;
	white-space: nowrap;
	text-overflow: ellipsis;
	overflow: hidden;
	color: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
}

.main.matching {
	background: var(--builderMatchingColor);
}

.main.childless {
	margin-left: 24px;
}

.toggleChildren {
	border-radius: 50%;
	height: 24px;
	width: 24px;
	min-width: 24px;
	display: flex;
	align-items: center;
	justify-content: center;
	cursor: pointer;
	margin-right: 4px;
	margin-left: -4px;
}

.toggleChildren:hover {
	background: var(--builderSubtleSeparatorColor);
}

.selected {
	background: var(--builderSelectedColor);
}

.type {
	color: black;
}

.preview {
	font-style: italic;
}

.main:not(.selected):hover {
	background: var(--builderSubtleHighlightColor);
}
.main:focus {
	outline: none;
}
.main:not(.selected):focus {
	background: var(--builderSubtleHighlightColor);
}

.children {
	margin-left: 12px;
}
</style>
