<template>
	<template v-if="isJSONObject(data) || isJSONArray(data)">
		<BaseJsonViewerCollapsible
			v-if="isRoot"
			open
			:data="data"
			@toggle="$emit('toggle', { path: [], open: $event })"
		>
			<BaseJsonViewerObject
				:data="data"
				:path="path"
				:opened-level="openedLevel"
				@toggle="$emit('toggle', $event)"
			/>
		</BaseJsonViewerCollapsible>
		<BaseJsonViewerObject
			v-else
			:data="data"
			:path="path"
			:opened-level="openedLevel"
			@toggle="$emit('toggle', $event)"
		/>
	</template>
	<BaseJsonViewerValue v-else-if="isJSONValue(data)" :data="data" />
</template>

<script lang="ts">
export type JsonValue = string | number | boolean | null;

export type JsonData = JsonValue | { [x: string]: JsonData } | JsonData[];

export type JsonPath = string[];

export type JsonViewerTogglePayload = { path: JsonPath; open: boolean };
</script>

<script setup lang="ts">
/**
 * This component will detect the shape of the JSON and redirect the right dedicated component.
 */
import { PropType, computed } from "vue";
import {
	isJSONArray,
	isJSONObject,
	isJSONValue,
	jsonViewerToggleEmitDefinition,
} from "./BaseJsonViewer.utils";
import BaseJsonViewerCollapsible from "./BaseJsonViewerCollapsible.vue";
import BaseJsonViewerObject from "./BaseJsonViewerObject.vue";
import BaseJsonViewerValue from "./BaseJsonViewerValue.vue";

const props = defineProps({
	data: {
		type: Object as PropType<JsonData>,
		required: true,
	},
	path: {
		type: Array as PropType<JsonPath>,
		default: () => [],
	},
	openedLevel: { type: Number, default: 0 },
});

defineEmits({
	toggle: jsonViewerToggleEmitDefinition,
});

const isRoot = computed(() => props.path.length === 0);
</script>
