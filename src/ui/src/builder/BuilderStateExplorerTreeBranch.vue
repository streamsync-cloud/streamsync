<template>
	<div class="BuilderStateExplorerTreeBranch">
		<template v-if="isRootValueObject">
			<div
				v-if="rootAccessors.length > 0"
				class="toggleChildren"
				@click="toggleChildrenVisible"
			>
				<i
					v-if="areChildrenVisible"
					class="ri-arrow-drop-up-line ri-lg"
				></i>
				<i
					v-if="!areChildrenVisible"
					class="ri-arrow-drop-down-line ri-lg"
				></i>
				{{ rootAccessors.at(-1) }}
			</div>
			<div v-if="areChildrenVisible" class="children">
				<template v-if="rootValue">
					<div v-for="childKey in sortedChildrenKeys" :key="childKey">
						<BuilderStateExplorerTreeBranch
							:root-accessors="[...rootAccessors, childKey]"
						></BuilderStateExplorerTreeBranch>
					</div>
				</template>
				<div v-else>
					<em>No state elements found.</em>
				</div>
			</div>
		</template>
		<div v-else class="valueContainer">
			{{ rootAccessors.at(-1) }}
			<span class="stateValueType"> : {{ rootValueType }}</span>
			<span class="stateValue">{{ displayableRootValue }}</span>
			<span class="spacer"></span>
			<button
				class="action"
				title="Copy reference to clipboard"
				@click="copyReferenceToClipboard()"
			>
				<i class="ri-braces-line ri-nd"></i>
			</button>
			<button
				class="action"
				title="Copy contents to clipboard"
				@click="copyContentsToClipboard()"
			>
				<i class="ri-file-copy-2-line ri-nd"></i>
			</button>
		</div>
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed, ref, Ref } from "vue";
import injectionKeys from "../injectionKeys";

// TODO test accessors with dots in evaluator

interface Props {
	rootAccessors: string[];
}

const props = defineProps<Props>();
const { rootAccessors } = toRefs(props);

const ss = inject(injectionKeys.core);
const areChildrenVisible: Ref<boolean> = ref(
	rootAccessors.value.length > 0 ? false : true,
);

function getStateValue(accessors: string[]) {
	let state = ss.getUserState();
	accessors.forEach((accessor) => {
		state = state[accessor];
	});
	return state;
}

const rootValue = computed(() => {
	return getStateValue(rootAccessors.value);
});

function isStateObject(v: any) {
	return typeof v == "object" && v !== null && !Array.isArray(v);
}

const isRootValueObject = computed(() => {
	const v = rootValue.value;
	return isStateObject(v);
});

const sortedChildrenKeys = computed(() => {
	if (!isRootValueObject.value) return [];
	const keys = Object.keys(rootValue.value);
	keys.sort((a, b) => {
		const aValue = getStateValue([...rootAccessors.value, a]);
		const bValue = getStateValue([...rootAccessors.value, b]);
		if (isStateObject(aValue) && !isStateObject(bValue)) return -1;
		if (!isStateObject(aValue) && isStateObject(bValue)) return 1;
		return a > b ? 1 : -1;
	});
	return keys;
});

const rootValueType = computed(() => {
	const v = rootValue.value;
	if (Array.isArray(v)) return "array";
	return typeof rootValue.value;
});

const displayableRootValue = computed(() => {
	const MAX_VALUE_LENGTH = 50;
	const v = (rootValue.value ?? "null").toString();
	if (v.length > MAX_VALUE_LENGTH) {
		return v.substring(0, MAX_VALUE_LENGTH) + "...";
	}
	return v;
});

function toggleChildrenVisible() {
	areChildrenVisible.value = !areChildrenVisible.value;
}

function copyReferenceToClipboard() {
	const stateRef = rootAccessors.value.join(".");
	navigator.clipboard.writeText(stateRef);
}

function copyContentsToClipboard() {
	const content = rootValue.value?.toString();
	navigator.clipboard.writeText(content);
}
</script>

<style scoped>
@import "./sharedStyles.css";

.toggleChildren {
	margin-left: -5px;
	cursor: pointer;
}

.toggleChildren ~ .children {
	margin-top: 16px;
}

.children {
	display: flex;
	flex-direction: column;
	gap: 16px;
	margin-left: v-bind('rootAccessors.length > 0 ? "16px" : "0"');
}
.valueContainer {
	display: flex;
	gap: 4px;
	align-items: center;
	white-space: nowrap;
}

.stateValueType {
	color: var(--builderSecondaryTextColor);
}

.stateValue {
	background: var(--builderSubtleSeparatorColor);
	padding: 4px;
	font-size: 0.7rem;
	margin-left: 4px;
	flex: 1 1 auto;
	overflow: hidden;
}

.action {
	background-color: var(--builderBackgroundColor);
	padding: 4px;
	border-radius: 50%;
	min-width: 16px;
	min-height: 16px;
}
</style>
