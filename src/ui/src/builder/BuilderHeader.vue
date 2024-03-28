<template>
	<div class="BuilderHeader">
		<img src="../assets/logo.svg" alt="Streamsync logo" />
		<BuilderSwitcher
			:options="{
				ui: { desc: 'User Interface', icon: 'ri-brush-line' },
				code: { desc: 'Code', icon: 'ri-code-line' },
				preview: { desc: 'Preview', icon: 'ri-pages-line' },
			}"
			:fn="
				(optionId: 'ui' | 'code' | 'preview') => {
					ssbm.setMode(optionId);
					if (ssbm.getMode() != 'preview') return;
					ssbm.setSelection(null);
				}
			"
		></BuilderSwitcher>
		<div class="undoRedo">
			<button
				class="undo"
				:title="
					undoRedoSnapshot.isUndoAvailable
						? `Undo ${undoRedoSnapshot.undoDesc}`
						: 'Nothing to undo'
				"
				:disabled="!undoRedoSnapshot.isUndoAvailable"
				@click="undo()"
			>
				<i class="ri-arrow-go-back-line"></i>
				Undo
			</button>
			<button
				class="redo"
				:title="
					undoRedoSnapshot.isRedoAvailable
						? `Redo ${undoRedoSnapshot.redoDesc}`
						: 'Nothing to redo'
				"
				:disabled="!undoRedoSnapshot.isRedoAvailable"
				@click="redo()"
			>
				<i class="ri-arrow-go-forward-line"></i>
				Redo
			</button>
		</div>
		<div>
			<button @click="showStateExplorer">
				<i class="ri-eye-line"></i>View state
			</button>
			<BuilderModal
				v-if="isStateExplorerShown"
				:close-action="customHandlerModalCloseAction"
				icon="eye"
				modal-title="State Explorer"
			>
				<BuilderStateExplorer></BuilderStateExplorer>
			</BuilderModal>
		</div>
		<div class="gap"></div>
		<div
			class="syncHealth"
			:class="ss.syncHealth.value"
			:title="syncHealthStatus()"
			@click="animate"
		>
			<i ref="syncHealthIcon" class="ri-refresh-line ri-lg icon"></i
			><span v-if="ss.syncHealth.value == 'offline'">Offline</span>
		</div>
	</div>
</template>

<script setup lang="ts">
import { Ref, computed, inject, ref } from "vue";
import BuilderSwitcher from "./BuilderSwitcher.vue";
import { useComponentActions } from "./useComponentActions";
import BuilderModal, { ModalAction } from "./BuilderModal.vue";
import injectionKeys from "../injectionKeys";
import BuilderStateExplorer from "./BuilderStateExplorer.vue";

const syncHealthIcon = ref(null);
const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { undo, redo, getUndoRedoSnapshot } = useComponentActions(ss, ssbm);
const isStateExplorerShown: Ref<boolean> = ref(false);

const undoRedoSnapshot = computed(() => getUndoRedoSnapshot());

const animate = () => {
	const iconEl: HTMLElement = syncHealthIcon.value;
	iconEl.classList.remove("beingAnimated");
	iconEl.offsetWidth;
	iconEl.classList.add("beingAnimated");
};

const syncHealthStatus = () => {
	switch (ss.syncHealth.value) {
		case "offline":
			return "Offline. Not syncing.";
		case "connected":
			return "Online. Syncing...";
		case "idle":
			return "Sync not initialised.";
	}
};

function showStateExplorer() {
	isStateExplorerShown.value = true;
}

const customHandlerModalCloseAction: ModalAction = {
	desc: "Close",
	fn: () => {
		isStateExplorerShown.value = false;
	},
};
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderHeader {
	background: var(--builderHeaderBackgroundColor);
	color: white;
	padding: 0 12px 0 16px;
	display: flex;
	align-items: center;
	gap: 16px;
	padding-top: 1px;
	border-bottom: 1px solid var(--builderAreaSeparatorColor);
}

.BuilderHeader img {
	width: 28px;
}

.undoRedo {
	display: flex;
	align-items: center;
	gap: 8px;
}
.BuilderHeader .gap {
	flex: 1 0 auto;
}

.syncHealth {
	background: var(--builderHeaderBackgroundHoleColor);
	border-radius: 18px;
	padding-left: 16px;
	padding-right: 16px;
	height: 32px;
	display: flex;
	gap: 8px;
	align-items: center;
	transition:
		color,
		background-color 0.5s ease-in-out;
}

.syncHealth.offline {
	background: var(--builderErrorColor);
}

.syncHealth.connected {
	color: var(--builderAccentColor);
}

.syncHealth .icon {
	transform-origin: center;
}

.syncHealth .icon.beingAnimated {
	animation-name: activate;
	animation-duration: 1s;
	animation-timing-function: ease-in-out;
}

@keyframes activate {
	0% {
		transform: rotate(0deg);
	}
	100% {
		transform: rotate(360deg);
	}
}

button {
	color: #ffffff;
}
</style>
