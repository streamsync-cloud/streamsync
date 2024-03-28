<template>
	<div
		ref="builderEditor"
		class="BuilderEditor"
		:class="{
			dark: theme == 'vs-dark',
			light: theme == 'vs-light',
			activeLog: isLogActive,
		}"
	>
		<div class="editor">
			<div class="windowBar">
				<div class="icon"><i class="ri-code-line ri-lg"></i></div>
				<div class="title">Code Editor</div>
				<button
					class="windowAction"
					tabindex="0"
					:title="(theme == 'vs-light' ? 'Dark' : 'Light') + ' theme'"
					@click="toggleTheme"
				>
					<i
						v-show="theme == 'vs-dark'"
						class="ri-sun-line ri-lg"
					></i>
					<i
						v-show="theme == 'vs-light'"
						class="ri-moon-line ri-lg"
					></i>
				</button>
			</div>
			<div class="codeActions">
				<button
					:disabled="editorDisabled"
					:title="`Save and run (${modifierKeyName}+s)`"
					@click="save"
				>
					<i class="ri-save-line"></i>{{ "Save and run" }}
				</button>
				<div v-if="statusMessage" class="statusMessage">
					<div v-if="statusMessage.ok === true" class="statusOk ok">
						<i class="ri-check-line"></i>
					</div>
					<div
						v-else-if="statusMessage.ok === false"
						class="statusOk notOk"
					>
						<i class="ri-error-warning-line"></i>
					</div>
					<div
						v-else-if="statusMessage.ok === 'processing'"
						class="statusOk processing"
					>
						<i class="ri-loader-3-line"></i>
					</div>
					{{ statusMessage.message }}
				</div>
			</div>
			<div ref="editorContainer" class="editorContainer"></div>
		</div>
		<div class="log">
			<div class="windowBar">
				<div class="icon"><i class="ri-booklet-line"></i></div>
				<div class="title">
					Log <span class="countLabel">{{ logEntries.length }}</span>
				</div>
				<button
					class="windowAction"
					tabindex="0"
					title="Clear log"
					@click="ssbm.clearLogEntries"
				>
					<i class="ri-delete-bin-line"></i>
				</button>
				<button
					class="windowAction"
					tabindex="0"
					:title="
						(isLogActive ? 'Hide' : 'Show') +
						` log (${modifierKeyName}+j)`
					"
					@click="toggleLog"
				>
					<i
						v-show="!isLogActive"
						class="ri-arrow-drop-up-line ri-lg"
					></i>
					<i
						v-show="isLogActive"
						class="ri-arrow-drop-down-line ri-lg"
					></i>
				</button>
			</div>
			<div v-if="isLogActive" class="entryContainer">
				<div
					v-for="(logEntry, index) in logEntries"
					:key="index"
					class="entry"
				>
					<div class="icon" :class="logEntry.type">
						<i
							:class="logEntryTypeIcon[logEntry.type]"
							class="ri-xl"
						></i>
					</div>
					<div class="content">
						<div class="header">
							<span class="title"
								>{{ logEntry.title
								}}{{
									logEntry.repeated > 0
										? ` · Repeated ${logEntry.repeated} times`
										: ""
								}}</span
							>
							<span class="time">{{
								logEntry.timestampReceived.toLocaleTimeString()
							}}</span>
						</div>
						<div class="message">
							{{ logEntry.message }}
							<div v-if="logEntry.code" class="codeContainer">
								<code>{{ logEntry.code }}</code>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import * as monaco from "monaco-editor";

import {
	inject,
	onMounted,
	onUnmounted,
	Ref,
	ref,
	watch,
	nextTick,
	computed,
	ComputedRef,
} from "vue";
import injectionKeys from "../injectionKeys";
import { isPlatformMac } from "../core/detectPlatform";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const builderEditor: Ref<HTMLElement> = ref(null);
const editorContainer: Ref<HTMLElement> = ref(null);
const editorDisabled: Ref<boolean> = ref(false);
let editor: monaco.editor.IStandaloneCodeEditor = null;
const modifierKeyName = isPlatformMac() ? "⌘ Cmd" : "Ctrl";

const theme: Ref<string> = ref(
	localStorage.getItem("currentTheme") || "vs-light",
);

const isLogActive: Ref<boolean> = ref(ssbm.getLogEntryCount() > 0);
const sessionTimestamp: ComputedRef<number> = computed(() =>
	ss.getSessionTimestamp(),
);

type StatusMessage = {
	ok: boolean | "processing";
	message: string;
};

const statusMessage: Ref<StatusMessage> = ref(null);

const logEntryTypeIcon: Record<string, string> = {
	error: "ri-error-warning-fill",
	info: "ri-information-fill",
};

const logEntries = computed(() => {
	return ssbm.getLogEntries();
});

const handleLogEntry = () => {
	isLogActive.value = true;
};

function handleKeydown(ev: KeyboardEvent) {
	const isModifierKeyActive = isPlatformMac() ? ev.metaKey : ev.ctrlKey;

	if (ev.key === "s" && isModifierKeyActive) {
		ev.preventDefault();
		save();
		return;
	}

	if (ev.key === "j" && isModifierKeyActive) {
		ev.preventDefault();
		toggleLog();
		return;
	}
}

onMounted(() => {
	document.addEventListener("keydown", handleKeydown);

	// Subscribe to new log entries to open log section, but ignore content of log entry.

	ss.addMailSubscription("logEntry", handleLogEntry);
	const targetEl = editorContainer.value;
	editor = monaco.editor.create(targetEl, {
		value: ss.getRunCode(),
		language: "python",
		theme: theme.value,
	});
	editor.getModel().onDidChangeContent(() => {
		statusMessage.value = null;
	});
	window.addEventListener("resize", updateDimensions.bind(this));
});

onUnmounted(() => {
	document.removeEventListener("keydown", handleKeydown);
	window.removeEventListener("resize", updateDimensions.bind(this));
});

watch(
	() => ss.getRunCode(),
	(newRunCode) => {
		editor.getModel().setValue(newRunCode);
	},
);

watch(
	() => ssbm.getMode(),
	(newMode) => {
		if (newMode !== "code") return;
		nextTick(() => {
			editor.layout();
		});
	},
);

watch(sessionTimestamp, () => {
	enableEditor();
});

const disableEditor = () => {
	editorDisabled.value = true;
	editor.updateOptions({ readOnly: true });
};

const enableEditor = () => {
	editorDisabled.value = false;
	editor.updateOptions({ readOnly: false });
};

const save = async () => {
	const editorCode = editor.getValue();
	statusMessage.value = {
		ok: "processing",
		message: `Processing...`,
	};
	try {
		disableEditor();
		await ss.sendCodeSaveRequest(editorCode);
	} catch (error) {
		statusMessage.value = {
			ok: false,
			message: `Code hasn't been saved. ${error}`,
		};
		enableEditor();
		return;
	}
	statusMessage.value = null;
};

const toggleLog = () => {
	isLogActive.value = !isLogActive.value;

	nextTick(() => {
		editor.layout();
	});
};

const toggleTheme = () => {
	if (theme.value == "vs-light") {
		theme.value = "vs-dark";
	} else {
		theme.value = "vs-light";
	}

	localStorage.setItem("currentTheme", theme.value);

	editor.updateOptions({
		theme: theme.value,
	});
};

const updateDimensions = () => {
	editor.layout();
};
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderEditor {
	width: 100%;
	height: 100%;
	display: grid;
	grid-template-columns: 1fr;
	grid-template-rows: 76fr 47fr;
	color: var(--builderPrimaryTextColor);
}

.BuilderEditor:not(.activeLog) {
	grid-template-rows: 76fr 48px;
}

.BuilderEditor.light {
	background: white;
}

.BuilderEditor.dark {
	background: #1e1e1e;
	--builderPrimaryTextColor: #f0f0f0;
	--builderSecondaryTextColor: #c0c0c0;
	--builderSubtleHighlightColorSolid: #2b2b2b;
	--builderSubtleSeparatorColor: rgba(255, 255, 255, 0.05);
}

.dark button {
	background: #1e1e1e;
	border: 1px solid var(--builderSubtleSeparatorColor);
	color: var(--builderPrimaryTextColor);
}

.editor {
	grid-column: 1;
	grid-row: 1;
	overflow: hidden;
	display: flex;
	flex-direction: column;
}

.editor .windowBar {
	flex: 0 0 auto;
}

.editor .codeActions {
	padding: 16px;
	display: flex;
	gap: 16px;
	flex: 0 0 auto;
	align-items: center;
}

.editor .codeActions button[disabled] {
	color: var(--builderDisabledColor);
}

.editor .saveTick {
	display: none;
	width: 16px;
	height: 16px;
	align-items: center;
	justify-content: center;
	border-radius: 50%;
	background: var(--builderDisabledColor);
	color: var(--builderBackgroundColor);
	transition: 0.2s all ease-in-out;
}

.editor .saveTick.saved {
	display: flex;
	background: var(--builderSecondaryTextColor);
}

.editor .statusMessage {
	display: flex;
	align-items: center;
	overflow: hidden;
}

.editor .statusMessage .statusOk {
	margin-right: 8px;
	display: flex;
	align-items: center;
}

.editor .statusMessage .statusOk.ok {
	color: var(--builderSuccessColor);
}

.editor .statusMessage .statusOk.notOk {
	color: var(--builderErrorColor);
}

.editor .editorContainer {
	flex: 1 0 0;
	overflow: hidden;
}

.log {
	overflow-y: auto;
	overflow-x: hidden;
	grid-column: 1;
	grid-row: 2;
	display: flex;
	flex-direction: column;
}

.entryContainer {
	flex: 1 0 auto;
}

.entryContainer:empty {
	display: flex;
	align-items: center;
	text-align: center;
	justify-content: center;
	padding: 16px;
}

.entryContainer:empty::after {
	content: "Exceptions and other relevant messages will be shown here. Also, you can include print statements in event handlers to create log entries.";
}

.entry {
	display: flex;
	align-items: center;
	border-top: 1px solid var(--builderSubtleSeparatorColor);
	width: 100%;
}

.entry .icon {
	flex: 0 0 72px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.entry .icon.error {
	color: #ff5d00;
}

.entry .icon.info {
	color: #0094d1;
}

.entry .content {
	flex: 1 1 auto;
	padding: 16px 16px 16px 0;
}

.entry .content .message {
	white-space: pre-wrap;
}

.entry .header {
	display: flex;
	margin-bottom: 4px;
}

.entry .header .title {
	flex: 1 0 auto;
	color: var(--builderSecondaryTextColor);
}

.entry .header .time {
	color: var(--builderSecondaryTextColor);
}

/* This pre tag tells the Prettier formatter to respect whitespace. */
.entry .content {
	font-family: inherit;
	margin: 0;
	white-space: pre-wrap;
}

.entry .content code {
	margin: 0;
	white-space: pre-wrap;
}

.entry .codeContainer {
	max-width: 100%;
	margin-top: 16px;
}

.entry code {
	margin: 0;
	width: 100%;
	max-height: 100%;
}
</style>
