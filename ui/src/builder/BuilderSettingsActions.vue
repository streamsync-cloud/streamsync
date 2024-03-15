<template>
	<div v-if="actions.length > 0" class="BuilderSettingsActions">
		<div class="sectionTitle">
			<i class="ri-equalizer-line ri-xl"></i>
			<h3>Actions</h3>
		</div>
		<div>
			<div class="propertyCategory">
				<div v-for="[fieldKey, action] in actions" :key="fieldKey">
					<div class="fieldWrapper">
						<button @click="action.handler">
							{{ action.name }}
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "../injectionKeys";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const selectedComponent = computed(() => {
	return ss.getComponentById(ssbm.getSelectedId());
});

const componentDefinition = ss.getComponentDefinitionById(
	selectedComponent.value.id,
);

const actions = computed(() => {
	if (!componentDefinition.value.actions) {
		return [];
	}
	return Object.entries(componentDefinition.value.actions);
});
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSettingsActions {
	padding: 24px;
}
</style>
