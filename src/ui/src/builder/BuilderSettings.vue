<template>
	<div v-if="ssbm.isSelectionActive()" class="BuilderSettings">
		<div class="windowBar">
			<div class="icon">
				<i class="ri-settings-3-line ri-lg"></i>
			</div>
			<div class="title">
				{{ componentDefinition.name }}
			</div>
			<button
				v-if="description || docsString"
				class="windowAction"
				tabindex="0"
				:title="(docsActive ? 'Hide' : 'Show') + ' inline docs'"
				@click="toggleDocs"
			>
				<i class="ri-question-line ri-lg"></i>
				<i v-if="docsActive" class="ri-arrow-drop-up-line ri-lg"></i>
				<i v-else class="ri-arrow-drop-down-line ri-lg"></i>
			</button>
			<button
				class="windowAction"
				tabindex="0"
				title="Close (Esc)"
				@click="closeSettings"
			>
				<i class="ri-close-line ri-lg"></i>
			</button>
		</div>

		<div v-if="docsActive" class="docs">
			<div v-if="description">{{ description }}</div>
			<div
				v-if="docsString"
				v-dompurify-html="generateUnsanitisedMarkdownHtml()"
				class="markdown"
			></div>
		</div>

		<div v-if="readonly" class="warning cmc-warning">
			<i class="ri-error-warning-line ri-xl"></i>
			<span>
				This component is instantiated in code. All settings in this
				panel are read-only and cannot be edited.
			</span>
		</div>

		<div class="sections" :inert="readonly">
			<BuilderSettingsProperties></BuilderSettingsProperties>
			<BuilderSettingsBinding v-if="isBindable"></BuilderSettingsBinding>
			<BuilderSettingsHandlers></BuilderSettingsHandlers>
			<BuilderSettingsVisibility></BuilderSettingsVisibility>
		</div>

		<div class="debug">
			Component id:
			{{ ssbm.getSelectedId() }}
		</div>
	</div>
</template>

<script setup lang="ts">
import { marked } from "marked";
import { inject, computed, ref, watch } from "vue";
import injectionKeys from "../injectionKeys";

import BuilderSettingsHandlers from "./BuilderSettingsHandlers.vue";
import BuilderSettingsProperties from "./BuilderSettingsProperties.vue";
import BuilderSettingsBinding from "./BuilderSettingsBinding.vue";
import BuilderSettingsVisibility from "./BuilderSettingsVisibility.vue";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const docsActive = ref(false);

const component = computed(() => ss.getComponentById(ssbm.getSelectedId()));
const readonly = computed(() => component.value.isCodeManaged);

const componentDefinition = computed(() => {
	const { type } = component.value;
	const definition = ss.getComponentDefinition(type);
	return definition;
});

const closeSettings = () => {
	ssbm.setSelection(null);
};

watch(component, (newComponent) => {
	if (!newComponent) closeSettings();
});

const toggleDocs = () => {
	docsActive.value = !docsActive.value;
};

const isBindable = computed(() =>
	Object.values(componentDefinition.value?.events ?? {}).some(
		(e) => e.bindable,
	),
);

const description = computed(() => {
	if (!componentDefinition.value?.description) return;
	return componentDefinition.value.description.trim();
});

const docsString = computed(() => {
	if (!componentDefinition.value?.docs) return;
	return componentDefinition.value.docs.trim();
});

const generateUnsanitisedMarkdownHtml = () => {
	return marked.parse(docsString.value);
};
</script>

<style scoped>
@import "./sharedStyles.css";
.BuilderSettings {
	font-size: 0.7rem;
	background: var(--builderBackgroundColor);
}
.docs {
	font-size: 0.75rem;
	padding: 24px;
	line-height: 1.5;
	background: var(--builderSubtleHighlightColorSolid);
	border-top: 1px solid var(--builderSubtleSeparatorColor);
	white-space: pre-wrap;
}

.docs div:not(:first-child) {
	margin-top: 16px;
	border-top: 1px solid var(--builderSubtleSeparatorColor);
	padding-top: 16px;
}

.sections {
	background: var(--builderBackgroundColor);
}

.sections[inert] {
	opacity: 0.7;
}

.sections > *:not(:first-child) {
	border-top: 1px solid var(--builderSeparatorColor);
}

.debug {
	color: var(--builderSecondaryTextColor);
	border-top: 1px solid var(--builderSeparatorColor);
	padding: 24px;
}

.warning {
	display: flex;
	align-items: center;
	background: var(--builderWarningColor);
	color: var(--builderWarningTextColor);
	border-radius: 4px;
	gap: 12px;
	margin: 12px 12px 0;
	padding: 12px;
}

/*
Markdown styling
*/

.markdown:deep() pre {
	background-color: var(--builderSubtleSeparatorColor);
	font-family: monospace;
	padding: 8px;
	border-radius: 4px;
}

.markdown:deep() code {
	background-color: var(--builderSubtleSeparatorColor);
	font-family: monospace;
	padding: 2px;
}

.markdown:deep() pre > code {
	background-color: unset;
}
</style>
