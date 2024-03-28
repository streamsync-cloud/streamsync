<template>
	<div
		class="CoreSidebar"
		:style="rootStyle"
		:class="{
			collapsed: isCollapsed,
		}"
	>
		<div class="collapserContainer">
			<div class="collapser" @click="toggleCollapsed">
				<IconGen
					class="collapserArrow"
					icon-key="collapseArrow"
				></IconGen>
			</div>
		</div>
		<div class="container" data-streamsync-container>
			<slot></slot>
		</div>
	</div>
</template>

<script lang="ts">
import { Component, FieldCategory, FieldType } from "../../streamsyncTypes";
import {
	accentColor,
	primaryTextColor,
	secondaryTextColor,
	containerBackgroundColor,
	containerShadow,
	separatorColor,
	buttonColor,
	buttonTextColor,
	buttonShadow,
	cssClasses,
} from "../../renderer/sharedStyleFields";

const description =
	"A container component that organises its children in a sidebar. Its parent must be a Page component.";

export default {
	streamsync: {
		name: "Sidebar",
		description,
		positionless: true,
		allowedParentTypes: ["page"],
		allowedChildrenTypes: ["*"],
		category: "Layout",
		fields: {
			startCollapsed: {
				name: "Start collapsed",
				type: FieldType.Text,
				category: FieldCategory.Style,
				default: "no",
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			sidebarBackgroundColor: {
				name: "Background",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
				default: "rgba(255, 255, 255, 0.3)",
			},
			accentColor,
			primaryTextColor,
			secondaryTextColor,
			containerBackgroundColor,
			containerShadow,
			separatorColor,
			buttonColor,
			buttonTextColor,
			buttonShadow,
			cssClasses,
		},
	},
};
</script>
<script setup lang="ts">
import { computed, inject, onMounted, Ref, ref, watch } from "vue";
import injectionKeys from "../../injectionKeys";
import IconGen from "../../renderer/IconGen.vue";

const fields = inject(injectionKeys.evaluatedFields);
const isCollapsed: Ref<boolean> = ref(fields.startCollapsed.value == "yes");
const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const componentId = inject(injectionKeys.componentId);
const selectedId = computed(() => ssbm?.getSelectedId());

const toggleCollapsed = () => {
	isCollapsed.value = !isCollapsed.value;
};

const rendererTop = ref(0);

const rootStyle = computed(() => {
	return {
		"max-height": `calc(100vh - ${rendererTop.value}px)`,
	};
});

watch(selectedId, (newSelectedId) => {
	if (!newSelectedId) return;
	if (!checkIfSidebarIsParent(newSelectedId)) return;
	isCollapsed.value = false;
});

const checkIfSidebarIsParent = (childId: Component["id"]): boolean => {
	const child = ss.getComponentById(childId);
	if (!child || child.type == "root") return false;
	if (child.parentId == componentId) return true;
	return checkIfSidebarIsParent(child.parentId);
};

onMounted(() => {
	const rendererEl: HTMLElement =
		document.querySelector(".ComponentRenderer");
	rendererTop.value =
		document.body.clientHeight - rendererEl.parentElement.clientHeight;
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreSidebar {
	overflow: auto;
	padding: 16px;
	border-right: 1px solid var(--separatorColor);
	position: sticky;
	top: 0;
	background-color: var(--sidebarBackgroundColor);
}

.CoreSidebar:not(.collapsed) {
	width: 20vw;
	max-width: 300px;
}

.CoreSidebar.collapsed > .container {
	display: none;
}

.collapserContainer {
	display: flex;
	justify-content: right;
	margin-bottom: 16px;
}

.collapserContainer > .collapser {
	flex: 0 0 32px;
	min-width: 32px;
	border-radius: 16px;
	padding: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
	stroke: var(--primaryTextColor);
	border: 1px solid var(--separatorColor);
}

.collapserContainer .collapserArrow {
	transition: all 0.5s ease-in-out;
	transform: rotate(0deg);
}

.CoreSidebar.collapsed .collapserArrow {
	transform: rotate(180deg);
}

.collapserContainer > .collapser:hover {
	background: var(--separatorColor);
}

@media only screen and (max-width: 768px) {
	.CoreSidebar {
		min-width: 100%;
		border-right: 0;
		border-bottom: 1px solid var(--separatorColor);
	}

	.CoreSidebar.collapsed > .collapserContainer {
		margin-bottom: 0;
	}

	.collapserContainer > .collapser {
		transform: rotate(90deg);
	}
}
</style>
