<template>
	<div v-if="ssbm.isSelectionActive()" class="BuilderSettingsVisibility">
		<div class="sectionTitle">
			<i class="ri-eye-line ri-xl"></i>
			<h3>Visibility</h3>
		</div>
		<div class="main">
			<div class="chipStack">
				<div
					class="chip"
					:class="{
						active:
							typeof component.visible == 'undefined' ||
							component.visible === true,
					}"
					@click="() => setVisibleValue(component.id, true)"
				>
					Yes
				</div>
				<div
					class="chip"
					:class="{ active: component.visible === false }"
					@click="() => setVisibleValue(component.id, false)"
				>
					No
				</div>
				<div
					class="chip"
					:class="{ active: typeof component.visible === 'string' }"
					@click="() => setVisibleValue(component.id, '')"
				>
					Custom
				</div>
			</div>
			<div
				v-if="typeof component.visible === 'string'"
				class="fieldWrapper"
			>
				<span class="name">Visibility value</span>
				<input
					:value="component.visible"
					type="text"
					class="content"
					placeholder="my_visibility_state_value"
					@input="
						(ev: Event) =>
							setVisibleValue(
								component.id,
								(ev.target as HTMLInputElement).value,
							)
					"
				/>
				<div class="desc">
					Reference a state or context element that will evaluate to
					true or false. Reference the element directly, i.e. use
					"my_var" instead of "@{my_var}".
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setVisibleValue } = useComponentActions(ss, ssbm);

const component = computed(() => ss.getComponentById(ssbm.getSelectedId()));
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSettingsVisibility {
	padding: 24px;
}

.main {
	margin-top: 16px;
}

input {
	padding: 16px 12px 12px 12px;
}
</style>
