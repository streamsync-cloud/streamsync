<template>
	<div class="BuilderApp" tabindex="-1">
		<div class="mainGrid">
			<BuilderHeader class="builderHeader"></BuilderHeader>
			<div v-if="builderMode !== 'preview'" class="sidebar">
				<BuilderSidebar></BuilderSidebar>
			</div>
			<div
				class="builderMain"
				:class="{
					buildMode: builderMode !== 'preview',
					previewMode: builderMode === 'preview',
				}"
			>
				<div class="rendererWrapper">
					<ComponentRenderer
						class="componentRenderer"
						:class="{
							settingsOpen:
								ssbm.isSelectionActive() &&
								!ssbm.isSettingsBarCollapsed(),
						}"
						@dragover="handleRendererDragover"
						@dragstart="handleRendererDragStart"
						@dragend="handleRendererDragEnd"
						@drop="handleRendererDrop"
						@click.capture="handleRendererClick"
					>
					</ComponentRenderer>
				</div>

				<div class="floatingContainer">
					<div class="floatingSticky">
						<div
							v-if="ssbm.isSelectionActive()"
							class="settingsHiderTab"
							@click="
								ssbm.setSettingsBarCollapsed(
									!ssbm.isSettingsBarCollapsed(),
								)
							"
						>
							<i
								v-if="ssbm.isSettingsBarCollapsed()"
								class="ri-settings-3-line ri-lg"
							></i>
							<i
								v-if="!ssbm.isSettingsBarCollapsed()"
								class="ri-arrow-drop-right-line ri-lg"
							></i>
						</div>
						<div
							v-if="ssbm.isSelectionActive()"
							:key="selectedId ?? 'noneSelected'"
							class="settingsBar"
							:class="{
								collapsed: ssbm.isSettingsBarCollapsed(),
							}"
						>
							<BuilderSettings></BuilderSettings>
						</div>

						<div v-show="builderMode == 'code'" class="codeBar">
							<BuilderEditor></BuilderEditor>
						</div>
					</div>
				</div>
			</div>
		</div>
		<!-- INSTANCE TRACKERS -->

		<template v-if="builderMode !== 'preview'">
			<BuilderInstanceTracker
				v-if="ssbm.isSelectionActive()"
				:key="selectedInstancePath"
				class="shortcutsTracker"
				:prevent-settings-bar-overlap="true"
				:instance-path="selectedInstancePath"
				:vertical-offset-pixels="-48"
				data-streamsync-cage
				@dragstart="handleRendererDragStart"
				@dragend="handleRendererDragEnd"
			>
				<BuilderComponentShortcuts
					draggable="true"
					:component-id="selectedId"
					:instance-path="selectedInstancePath"
				></BuilderComponentShortcuts>
			</BuilderInstanceTracker>
			<template v-if="candidateId && !isCandidacyConfirmed">
				<BuilderInstanceTracker
					:key="candidateInstancePath"
					class="insertionOverlayTracker"
					:is-off-bounds-allowed="true"
					:instance-path="candidateInstancePath"
					:match-size="true"
				>
					<BuilderInsertionOverlay></BuilderInsertionOverlay>
				</BuilderInstanceTracker>
				<BuilderInstanceTracker
					:key="candidateInstancePath"
					class="insertionLabelTracker"
					:instance-path="candidateInstancePath"
					:vertical-offset-pixels="-48"
				>
					<BuilderInsertionLabel>
						{{
							ss.getComponentDefinition(
								ss.getComponentById(candidateId).type,
							).name
						}}
					</BuilderInsertionLabel>
				</BuilderInstanceTracker>
			</template>
		</template>
		<!-- MODAL -->

		<div id="modal"></div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted } from "vue";
import { useDragDropComponent } from "./useDragDropComponent";
import { useComponentActions } from "./useComponentActions";
import BuilderHeader from "./BuilderHeader.vue";
import BuilderSettings from "./BuilderSettings.vue";
import BuilderEditor from "./BuilderEditor.vue";
import BuilderSidebar from "./BuilderSidebar.vue";
import ComponentRenderer from "../renderer/ComponentRenderer.vue";
import BuilderComponentShortcuts from "./BuilderComponentShortcuts.vue";
import injectionKeys from "../injectionKeys";
import BuilderInstanceTracker from "./BuilderInstanceTracker.vue";
import BuilderInsertionOverlay from "./BuilderInsertionOverlay.vue";
import BuilderInsertionLabel from "./BuilderInsertionLabel.vue";
import { isPlatformMac } from "../core/detectPlatform";
import { getClosestComponent } from "./helpers";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const {
	candidateId,
	candidateInstancePath,
	isCandidacyConfirmed,
	dropComponent,
	assignInsertionCandidacy,
	removeInsertionCandidacy,
} = useDragDropComponent(ss);
const {
	createAndInsertComponent,
	undo,
	redo,
	moveComponent,
	moveComponentUp,
	moveComponentDown,
	cutComponent,
	isPasteAllowed,
	isCopyAllowed,
	isCutAllowed,
	isDeleteAllowed,
	isGoToParentAllowed,
	pasteComponent,
	copyComponent,
	removeComponentSubtree,
	goToParent,
} = useComponentActions(ss, ssbm);

const builderMode = computed(() => ssbm.getMode());

const selectedId = computed(() => ssbm.getSelection()?.componentId);
const selectedInstancePath = computed(() => ssbm.getSelection()?.instancePath);

function handleKeydown(ev: KeyboardEvent): void {
	if (ev.key == "Escape") {
		ssbm.setSelection(null);
		return;
	}

	const isModifierKeyActive = isPlatformMac() ? ev.metaKey : ev.ctrlKey;
	const targetEl = ev.target as HTMLElement;
	if (targetEl.closest("textarea, input, select")) return;

	if (ev.key == "z" && isModifierKeyActive) {
		ev.preventDefault();
		undo();
		return;
	}
	if (ev.key == "y" && isModifierKeyActive) {
		ev.preventDefault();
		redo();
		return;
	}

	if (!ssbm.isSelectionActive()) return;
	const { componentId: selectedId, instancePath: selectedInstancePath } =
		ssbm.getSelection();

	if (ev.key == "Delete") {
		if (!isDeleteAllowed(selectedId)) return;
		removeComponentSubtree(selectedId);
		return;
	}
	if (ev.key == "ArrowUp" && isModifierKeyActive && ev.shiftKey) {
		if (!isGoToParentAllowed(selectedId)) return;
		goToParent(selectedId, selectedInstancePath);
		return;
	}
	if (ev.key == "ArrowUp" && isModifierKeyActive) {
		moveComponentUp(selectedId);
		return;
	}
	if (ev.key == "ArrowDown" && isModifierKeyActive) {
		moveComponentDown(selectedId);
		return;
	}
	if (ev.key == "v" && isModifierKeyActive) {
		if (!isPasteAllowed(selectedId)) return;
		pasteComponent(selectedId);
		return;
	}
	if (ev.key == "c" && isModifierKeyActive) {
		if (!isCopyAllowed(selectedId)) return;
		copyComponent(selectedId);
		return;
	}
	if (ev.key == "x" && isModifierKeyActive) {
		if (!isCutAllowed(selectedId)) return;
		cutComponent(selectedId);
		return;
	}
}

function handleRendererDragover(ev: DragEvent) {
	if (builderMode.value === "preview") return;
	assignInsertionCandidacy(ev);
}

function handleRendererDrop(ev: DragEvent) {
	if (builderMode.value === "preview") return;
	ssbm.setSelection(null);
	const dropInfo = dropComponent(ev);
	if (!dropInfo) return;
	const { draggedType, draggedId, parentId, position } = dropInfo;

	if (!draggedId) {
		createAndInsertComponent(draggedType, parentId, position);
	} else {
		moveComponent(draggedId, parentId, position);
	}
}

function handleRendererClick(ev: PointerEvent): void {
	if (builderMode.value === "preview") return;

	const targetEl: HTMLElement = getClosestComponent(
		ev.target as HTMLElement,
		"[data-streamsync-id]",
	);
	if (!targetEl) return;
	const targetId = targetEl.dataset.streamsyncId;
	const targetInstancePath = targetEl.dataset.streamsyncInstancePath;
	if (targetId !== ssbm.getSelectedId()) {
		ev.preventDefault();
		ev.stopPropagation();
		ssbm.setSelection(targetId, targetInstancePath);
	}
}

const handleRendererDragStart = (ev: DragEvent) => {
	if (builderMode.value === "preview") return;

	const targetEl: HTMLElement = getClosestComponent(
		ev.target as HTMLElement,
		"[data-streamsync-id]",
	);

	const componentId = targetEl.dataset.streamsyncId;
	const { type } = ss.getComponentById(componentId);

	ev.dataTransfer.setData(
		`application/json;streamsync=${type},${componentId}`,
		"{}",
	);
};

const handleRendererDragEnd = (ev: DragEvent) => {
	ssbm.setSelection(null);
	removeInsertionCandidacy(ev);
};

onMounted(() => {
	document.addEventListener("keydown", (ev) => handleKeydown(ev));
});
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderApp {
	--builderBackgroundColor: #ffffff;
	--builderAccentColor: #29cf00;
	--builderSuccessColor: #29cf00;
	--builderErrorColor: #ff3d00;
	--builderHeaderBackgroundColor: #353535;
	--builderHeaderBackgroundHoleColor: #202020;
	--builderPrimaryTextColor: rgba(0, 0, 0, 0.9);
	--builderSecondaryTextColor: rgba(0, 0, 0, 0.6);
	--builderAreaSeparatorColor: rgba(0, 0, 0, 0.2);
	--builderSeparatorColor: rgba(0, 0, 0, 0.1);
	--builderSubtleSeparatorColor: rgba(0, 0, 0, 0.05);
	--builderIntenseSeparatorColor: rgba(0, 0, 0, 0.2);
	--builderSelectedColor: rgba(210, 234, 244, 0.8);
	--builderMatchingColor: #f8dccc;
	--builderIntenseSelectedColor: #0094d1;
	--builderSubtleHighlightColor: rgba(0, 0, 0, 0.05);
	--builderSubtleHighlightColorSolid: #f2f2f2;
	--builderDisabledColor: rgb(180, 180, 180);
	--builderSidebarWidth: max(265px, 27vh);
	--builderSettingsWidth: max(265px, 27vh);
	--builderActionOngoingColor: rgba(0, 0, 0, 0.7);
	--builderTopBarHeight: 48px;
	font-size: 0.8rem;
	color: var(--builderPrimaryTextColor);
	font-family: "Inter";
	width: 100vw;
	height: 100vh;
	position: relative;
	overflow: hidden;
	background: var(--builderBackgroundColor);
}

.mainGrid {
	width: 100vw;
	height: 100vh;
	grid-template-columns: var(--builderSidebarWidth) 1fr;
	grid-template-rows: var(--builderTopBarHeight) 1fr;
	display: grid;
}

.builderHeader {
	grid-column: 1 / 3;
	grid-row: 1;
	z-index: 2;
}

.sidebar {
	grid-column: 1;
	grid-row: 2;
	min-height: 0;
	border-right: 1px solid var(--builderAreaSeparatorColor);
}

.builderMain {
	background: var(--builderBackgroundColor);
	overflow: hidden;
	position: relative;
}

.builderMain.buildMode {
	grid-column: 2;
	grid-row: 2;
}

.builderMain.previewMode {
	grid-column-start: 1;
	grid-column-end: 3;
	grid-row: 2;
}

.rendererWrapper {
	display: flex;
	flex-direction: column;
	height: 100%;
	overflow-y: auto;
}

.componentRenderer {
	min-height: 100%;
	flex: 1 0 auto;
}

.componentRenderer.settingsOpen {
	--notificationsDisplacement: calc(var(--builderSettingsWidth) + 24px);
}
.floatingContainer {
	position: absolute;
	z-index: 4;
	right: 0;
	top: 0;
	height: 100%;
	border-top: 1px solid var(--builderSeparatorColor);
	background: var(--builderBackgroundColor);
	box-shadow: 0 0 16px 0px rgba(0, 0, 0, 0.1);
}

.floatingSticky {
	position: sticky;
	top: 0;
	right: 0;
	display: flex;
	height: calc(100vh - 48px);
}

.settingsHiderTab {
	position: absolute;
	left: -23px;
	top: 108px;
	background: var(--builderBackgroundColor);
	padding-left: 2px;
	width: 24px;
	height: 48px;
	border-radius: 8px 0 0 8px;
	border-left: 1px solid var(--builderAreaSeparatorColor);
	border-top: 1px solid var(--builderAreaSeparatorColor);
	border-bottom: 1px solid var(--builderAreaSeparatorColor);
	border-right: 1px solid var(--builderSeparatorColor);
	box-shadow: 0px 0 16px 0px rgba(0, 0, 0, 0.1);
	z-index: 1;
	display: flex;
	justify-content: center;
	align-items: center;
	cursor: pointer;
}

.settingsHiderTab:hover {
	background: var(--builderSubtleHighlightColorSolid);
}

.settingsBar {
	z-index: 4;
	width: var(--builderSettingsWidth);
	min-height: 100%;
	overflow-y: auto;
	border-left: 1px solid var(--builderAreaSeparatorColor);
	background: var(--builderBackgroundColor);
}

.settingsBar.collapsed {
	display: none;
}

.codeBar {
	width: 50vw;
	height: 100%;
	border-left: 1px solid var(--builderAreaSeparatorColor);
}

@media (min-width: 1600px) {
	.buildMode .componentRenderer {
		width: calc(
			100vw - var(--builderSettingsWidth) - var(--builderSidebarWidth)
		);
	}

	.componentRenderer.settingsOpen {
		--notificationsDisplacement: 0;
	}

	.settingsHiderTab {
		display: none;
	}

	.settingsBar.collapsed {
		display: block;
	}
}

.shortcutsTracker,
.insertionLabelTracker {
	z-index: 3;
}

.insertionOverlayTracker {
	z-index: 1;
}

#modal {
	position: absolute;
	top: 0;
	left: 0;
	z-index: 10;
}
</style>
