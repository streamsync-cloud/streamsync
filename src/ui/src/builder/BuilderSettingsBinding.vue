<template>
	<div v-if="ssbm.isSelectionActive()" class="BuilderSettingsBinding">
		<div class="sectionTitle">
			<i class="ri-links-line ri-xl"></i>
			<h3>Binding</h3>
		</div>
		<div class="main">
			<div class="fieldWrapper">
				<span class="name">State element</span>
				<input
					:value="component.binding?.stateRef"
					type="text"
					class="content"
					placeholder="my_var"
					@input="
						(ev: Event) =>
							setBinding(
								component.id,
								(ev.target as HTMLInputElement).value,
							)
					"
				/>
				<div class="desc">
					Links this component to a state element, in a two-way
					fashion. Reference the state element directly, i.e. use
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
const { setBinding } = useComponentActions(ss, ssbm);

const component = computed(() => ss.getComponentById(ssbm.getSelectedId()));
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSettingsBinding {
	padding: 24px;
}

.main {
	margin-top: 16px;
}

input {
	padding: 16px 12px 12px 12px;
}
</style>
