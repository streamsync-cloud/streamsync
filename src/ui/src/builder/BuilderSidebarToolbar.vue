<template>
	<div class="BuilderSidebarToolbar">
		<div class="sectionTitle">
			<i class="ri-tools-line ri-xl"></i>
			<h3>Toolkit</h3>
		</div>
		<div class="categories">
			<template
				v-for="(categoryData, category) in categoriesData"
				:key="category"
			>
				<div v-if="categoryData.isVisible !== false" class="category">
					<div class="title">
						<i :class="categoryData.icon ?? 'ri-question-line'"></i>
						<h4>{{ category }}</h4>

						<div
							class="drop-arrow"
							@click="toggleCollapseCategory(category)"
						>
							<i
								class="ri-xl"
								:class="
									categoryData.isCollapsed
										? 'ri-arrow-drop-down-line'
										: 'ri-arrow-drop-up-line'
								"
							></i>
						</div>
					</div>

					<div v-show="!categoryData.isCollapsed" class="components">
						<div
							v-for="(
								definition, type
							) in definitionsByDisplayCategory[category]"
							:key="type"
							class="component button"
							:title="definition.description"
							draggable="true"
							:data-component-type="type"
							@dragend="handleDragEnd($event)"
							@dragstart="handleDragStart($event, type)"
						>
							{{ definition.name ?? type }}
							<i
								v-if="type.startsWith('custom_')"
								class="ri-collage-line ri-lg"
								title="(Custom component template)"
							></i>
						</div>
					</div>
				</div>
			</template>
		</div>
	</div>
</template>

<script setup lang="ts">
import { Ref, computed, inject, ref } from "vue";
import { useDragDropComponent } from "./useDragDropComponent";
import injectionKeys from "../injectionKeys";
import { Component, StreamsyncComponentDefinition } from "../streamsyncTypes";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { removeInsertionCandidacy } = useDragDropComponent(ss);

type CategoryData = {
	isVisible?: boolean;
	isCollapsed?: boolean;
	icon?: string;
};

const categoriesData: Ref<Record<string, CategoryData>> = ref({
	Root: {
		isVisible: false,
	},
	Layout: {
		icon: "ri-layout-line",
		isCollapsed: false,
	},
	Content: {
		icon: "ri-image-line",
		isCollapsed: false,
	},
	Input: {
		icon: "ri-keyboard-line",
		isCollapsed: false,
	},
	Embed: {
		icon: "ri-code-s-slash-line",
		isCollapsed: false,
	},
	Other: {
		icon: "ri-flow-chart",
		isCollapsed: false,
	},
});

function toggleCollapseCategory(categoryId: string) {
	const categoryData = categoriesData.value[categoryId];
	categoryData.isCollapsed = !categoryData.isCollapsed;
}

const definitionsByDisplayCategory = computed(() => {
	const types = ss.getSupportedComponentTypes();
	const result: Record<
		string,
		Record<string, StreamsyncComponentDefinition>
	> = {};

	types.map((type) => {
		const definition = ss.getComponentDefinition(type);
		const isMatch = Object.keys(categoriesData.value).includes(
			definition.category,
		);
		let displayCategory: string;
		if (!isMatch) {
			displayCategory = "Other";
		} else {
			displayCategory = definition.category;
		}
		if (!result[displayCategory]) {
			result[displayCategory] = {};
		}
		result[displayCategory][type] = definition;
	});

	return result;
});

const handleDragStart = (ev: DragEvent, type: Component["type"]) => {
	ssbm.setSelection(null);
	ev.dataTransfer.setData(`application/json;streamsync=${type},`, "{}");
};

const handleDragEnd = (ev: DragEvent) => {
	removeInsertionCandidacy(ev);
};
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSidebarToolbar {
	font-size: 0.7rem;
}

.BuilderSidebarToolbar > .sectionTitle {
	padding: 16px;
	position: sticky;
	top: 0;
	background: var(--builderBackgroundColor);
}

.categories {
	padding: 0 12px 12px 12px;
	flex: 1 1 auto;
	display: flex;
	flex-direction: column;
}

.category .title {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 8px;
	gap: 8px;
}

.category .title h4 {
	flex: 1 0 auto;
}

.category .components {
	padding: 4px 0 4px 0;
}

.component {
	padding: 8px;
	border-radius: 4px;
	cursor: grab;
	display: flex;
	align-items: center;
	gap: 4px;
}

.component:hover {
	background: var(--builderSubtleHighlightColor);
}

.drop-arrow {
	border-radius: 50%;
	min-width: 24px;
	min-height: 24px;
	display: flex;
	align-items: center;
	justify-content: center;
	cursor: pointer;
}

.drop-arrow:hover {
	background: var(--builderSubtleSeparatorColor);
}
</style>
