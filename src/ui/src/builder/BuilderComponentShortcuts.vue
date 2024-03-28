<template>
	<div
		v-if="shortcutsInfo"
		:draggable="shortcutsInfo?.isDraggable"
		class="BuilderComponentShortcuts"
		:data-streamsync-id="componentId"
	>
		<div class="type">
			{{ shortcutsInfo?.componentTypeName }}
		</div>
		<template v-if="!isAddMode">
			<div
				class="actionButton"
				title="Add child"
				:class="{
					enabled: shortcutsInfo?.isAddEnabled,
				}"
				@click="
					shortcutsInfo?.isAddEnabled
						? (isAddMode = !isAddMode)
						: undefined
				"
			>
				<i class="ri-add-line"></i>
			</div>
			<div
				class="actionButton"
				:title="`Move up (${modifierKeyName}+↑)`"
				:class="{
					enabled: shortcutsInfo?.isMoveUpEnabled,
				}"
				@click="
					shortcutsInfo?.isMoveUpEnabled
						? moveComponentUp(componentId)
						: undefined
				"
			>
				<i class="ri-arrow-up-line"></i>
			</div>
			<div
				class="actionButton"
				:title="`Move down (${modifierKeyName}+↓)`"
				:class="{
					enabled: shortcutsInfo?.isMoveDownEnabled,
				}"
				@click="
					shortcutsInfo?.isMoveDownEnabled
						? moveComponentDown(componentId)
						: undefined
				"
			>
				<i class="ri-arrow-down-line"></i>
			</div>

			<div
				class="actionButton"
				:title="`Cut (${modifierKeyName}+X)`"
				:class="{
					enabled: shortcutsInfo?.isCutEnabled,
				}"
				@click="
					shortcutsInfo?.isCutEnabled
						? cutComponent(componentId)
						: undefined
				"
			>
				<i class="ri-scissors-line"></i>
			</div>
			<div
				class="actionButton"
				:title="`Copy (${modifierKeyName}+C)`"
				:class="{
					enabled: shortcutsInfo?.isCopyEnabled,
				}"
				@click="
					shortcutsInfo?.isCopyEnabled
						? copyComponent(componentId)
						: undefined
				"
			>
				<i class="ri-file-copy-line"></i>
			</div>
			<div
				class="actionButton"
				:title="`Paste (${modifierKeyName}+V)`"
				:class="{
					enabled: shortcutsInfo?.isPasteEnabled,
				}"
				@click="
					shortcutsInfo?.isPasteEnabled
						? pasteComponent(componentId)
						: undefined
				"
			>
				<i class="ri-clipboard-line"></i>
			</div>
			<div
				class="actionButton"
				:title="`Go to parent (${modifierKeyName}+Shift+↑)`"
				:class="{
					enabled: shortcutsInfo?.isGoToParentEnabled,
				}"
				@click="
					shortcutsInfo?.isGoToParentEnabled
						? goToParent(componentId, instancePath)
						: undefined
				"
			>
				<i class="ri-parent-line"></i>
			</div>
			<div
				class="actionButton delete"
				data-automation-action="delete"
				title="Delete (Del)"
				:class="{
					enabled: shortcutsInfo?.isDeleteEnabled,
				}"
				@click="
					shortcutsInfo?.isDeleteEnabled
						? removeComponentSubtree(componentId)
						: undefined
				"
			>
				<i class="ri-delete-bin-line"></i>
			</div>
		</template>
		<template v-if="isAddMode">
			<div class="addDialog">
				<input
					type="text"
					list="validChildrenTypes"
					placeholder="Component..."
					@change="addComponent"
				/>
				<datalist id="validChildrenTypes">
					<option
						v-for="(definition, type) in validChildrenTypes"
						:key="type"
						:value="definition.name"
					>
						{{ definition.name }}
					</option>
				</datalist>
			</div>
		</template>
	</div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, Ref, ref, toRefs, watch } from "vue";
import { useComponentActions } from "./useComponentActions";
import { Component, StreamsyncComponentDefinition } from "../streamsyncTypes";
import injectionKeys from "../injectionKeys";
import { isPlatformMac } from "../core/detectPlatform";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const {
	createAndInsertComponent,
	moveComponentUp,
	moveComponentDown,
	cutComponent,
	pasteComponent,
	copyComponent,
	isAddAllowed,
	isCopyAllowed,
	isCutAllowed,
	isGoToParentAllowed,
	isPasteAllowed,
	isDeleteAllowed,
	isDraggingAllowed,
	getEnabledMoves,
	removeComponentSubtree,
	goToParent,
} = useComponentActions(ss, ssbm);

const props = defineProps<{
	componentId: Component["id"];
	instancePath: string;
}>();

const { componentId, instancePath } = toRefs(props);

const isAddMode = ref(false);

const shortcutsInfo: Ref<{
	componentTypeName: string;
	isAddEnabled: boolean;
	isMoveUpEnabled: boolean;
	isMoveDownEnabled: boolean;
	isCopyEnabled: boolean;
	isCutEnabled: boolean;
	isPasteEnabled: boolean;
	isGoToParentEnabled: boolean;
	isDeleteEnabled: boolean;
	isDraggable: boolean;
}> = ref(null);

const validChildrenTypes = computed(() => {
	const types = ss.getContainableTypes(componentId.value);
	const result: Record<string, StreamsyncComponentDefinition> = {};

	types.map((type) => {
		const definition = ss.getComponentDefinition(type);
		result[type] = definition;
	});

	return result;
});

function addComponent(event: Event) {
	const definitionName = (event.target as HTMLInputElement).value;
	const matchingTypes = Object.entries(validChildrenTypes.value).filter(
		([type, definition]) => {
			if (definition.name == definitionName) return true;
			return false;
		},
	);
	if (matchingTypes.length == 0) return;
	const type = matchingTypes[0][0];
	isAddMode.value = false;
	createAndInsertComponent(type, componentId.value);
}

function reprocessShorcutsInfo(): void {
	const component = ss.getComponentById(componentId.value);
	if (!component) return;
	const { up: isMoveUpEnabled, down: isMoveDownEnabled } = getEnabledMoves(
		componentId.value,
	);
	shortcutsInfo.value = {
		isAddEnabled: isAddAllowed(componentId.value),
		componentTypeName: ss.getComponentDefinition(component.type)?.name,
		isMoveUpEnabled,
		isMoveDownEnabled,
		isCopyEnabled: isCopyAllowed(componentId.value),
		isCutEnabled: isCutAllowed(componentId.value),
		isPasteEnabled: isPasteAllowed(componentId.value),
		isGoToParentEnabled: isGoToParentAllowed(componentId.value),
		isDeleteEnabled: isDeleteAllowed(componentId.value),
		isDraggable: isDraggingAllowed(componentId.value),
	};
}

watch(
	() => ss.getComponentById(componentId.value)?.position,
	async (newPosition) => {
		if (typeof newPosition == "undefined" || newPosition === null) return;
		reprocessShorcutsInfo();
	},
	{ flush: "post" },
);

const modifierKeyName = isPlatformMac() ? "⌘ Cmd" : "Ctrl";

onMounted(() => {
	reprocessShorcutsInfo();
});
</script>

<style scoped>
@import "./sharedStyles.css";
.BuilderComponentShortcuts {
	display: flex;
	border-radius: 18px;
	box-shadow: 0 0 8px -1px rgba(0, 0, 0, 0.6);
	background: var(--builderBackgroundColor);
	pointer-events: auto;
	overflow: hidden;
}

.type {
	display: flex;
	align-items: center;
	padding-left: 16px;
	padding-right: 16px;
	height: 36px;
	background: var(--builderSelectedColor);
}

[draggable="true"] .type {
	cursor: grab;
}

[draggable="true"] .type:active {
	cursor: grabbing;
}

.actionButton {
	width: 36px;
	height: 36px;
	display: flex;
	align-items: center;
	justify-content: center;
	color: var(--builderDisabledColor);
}

.actionButton:last-of-type {
	padding-right: 4px;
}

.actionButton.enabled {
	cursor: pointer;
	color: var(--builderPrimaryTextColor);
}

.actionButton.enabled.delete {
	color: var(--builderErrorColor);
}

.addDialog {
	display: flex;
	align-items: center;
	flex: 1 0 120px;
}

.addDialog input {
	flex: 1 0 auto;
	padding: 8px;
	height: 100%;
	outline: none;
	border: none;
}
</style>
