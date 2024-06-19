<template>
	<div class="WdsJsonViewerObject">
		<template
			v-for="([key, value], index) in Object.entries(data)"
			:key="index"
		>
			<!-- This is a single value, we display it as plain key/value text -->
			<div
				v-if="isJSONValue(value) || getJSONLength(value) === 0"
				class="WdsJsonViewerObject__value"
			>
				<span>{{ key }}</span
				>:
				<BaseJsonViewerValue :data="value" />
			</div>
			<!-- This is a an object -->
			<BaseJsonViewerCollapsible
				v-else
				:open="isOpen(key)"
				:title="key"
				:data="value"
				@toggle="toggleOpenedKey(key, $event)"
			>
				<BaseJsonViewer
					v-if="isOpen(key)"
					:data="value"
					:path="[...path, key]"
					:opened-level="openedLevel"
					@toggle="$emit('toggle', $event)"
				/>
			</BaseJsonViewerCollapsible>
		</template>
	</div>
</template>

<script setup lang="ts">
import { PropType, computed, ref, toRef, watch } from "vue";
import {
	getJSONLength,
	isJSONValue,
	jsonViewerToggleEmitDefinition,
} from "./BaseJsonViewer.utils";
import type { JsonData, JsonPath } from "./BaseJsonViewer.vue";
import BaseJsonViewer from "./BaseJsonViewer.vue";
import BaseJsonViewerCollapsible from "./BaseJsonViewerCollapsible.vue";
import BaseJsonViewerValue from "./BaseJsonViewerValue.vue";

const props = defineProps({
	data: {
		type: Object as PropType<{ [x: string]: JsonData } | JsonData>,
		required: true,
	},
	path: {
		type: Array as PropType<JsonPath>,
		default: () => [],
	},
	openedLevel: { type: Number, default: 0 },
});

const openedLevel = toRef(props, "openedLevel");

const emit = defineEmits({
	toggle: jsonViewerToggleEmitDefinition,
});

const openedKeys = ref<string[]>([]);

const currentLevel = computed(() => props.path.length + 1);

watch(
	openedLevel,
	() => {
		if (openedLevel.value === 0) {
			openedKeys.value = [];
			return;
		}

		const shouldAddKeys =
			openedLevel.value === -1 || openedLevel.value >= currentLevel.value;

		if (!shouldAddKeys) return;

		const keysToOpen = new Set([
			...openedKeys.value,
			...Object.keys(props.data),
		]);

		openedKeys.value = Array.from(keysToOpen);
	},
	{ immediate: true },
);

function toggleOpenedKey(key: string, open: boolean) {
	if (open) {
		openedKeys.value = [...openedKeys.value, key];
	} else {
		openedKeys.value = openedKeys.value.filter((k) => k !== key);
	}
	emit("toggle", { open, path: [...props.path, key] });
}

function isOpen(key: string) {
	return openedKeys.value.includes(String(key));
}
</script>

<style scoped>
.WdsJsonViewerObject {
	display: flex;
	flex-direction: column;
	gap: 4px;
}

.WdsJsonViewerObject__value {
	font-family: monospace;
	font-size: 12px;
	padding-left: 16px;

	display: flex;
	gap: 4px;
}
</style>
