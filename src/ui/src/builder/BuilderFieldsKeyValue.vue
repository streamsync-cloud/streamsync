<template>
	<div ref="rootEl" class="BuilderFieldsOptions" tabindex="-1">
		<div class="chipStackContainer">
			<div class="chipStack">
				<button
					class="chip"
					:class="{ active: mode == 'assisted' }"
					tabindex="0"
					@click="setMode('assisted')"
				>
					Static List
				</button>
				<button
					class="chip"
					tabindex="0"
					:class="{ active: mode == 'freehand' }"
					@click="setMode('freehand')"
				>
					JSON
				</button>
			</div>
		</div>

		<template v-if="mode == 'assisted'">
			<div class="staticList">
				<div
					v-for="(entryValue, entryKey) in assistedEntries"
					:key="entryKey"
					class="entry"
				>
					<div>{{ entryKey }} &middot; {{ entryValue }}</div>
					<button
						variant="subtle"
						@click="removeAssistedEntry(entryKey)"
					>
						<i class="ri-delete-bin-line"></i>
					</button>
				</div>
			</div>
			<div class="formAdd">
				<input
					ref="assistedKeyEl"
					v-model="formAdd.key"
					type="text"
					placeholder="Type a key..."
					@keydown.enter="addAssistedEntry"
				/>
				<input
					v-model="formAdd.value"
					type="text"
					placeholder="Type a value..."
					@keydown.enter="addAssistedEntry"
				/>
				<button @click="addAssistedEntry">
					<i class="ri-add-line"></i>Add
				</button>
			</div>
		</template>

		<template v-if="mode == 'freehand'">
			<BuilderFieldsObject
				:component-id="component.id"
				:field-key="fieldKey"
			></BuilderFieldsObject>
		</template>
	</div>
</template>

<script setup lang="ts">
import {
	nextTick,
	onMounted,
	Ref,
	ref,
	toRefs,
	inject,
	computed,
	watch,
} from "vue";
import { Component } from "../streamsyncTypes";
import BuilderFieldsObject from "./BuilderFieldsObject.vue";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(ss, ssbm);

const props = defineProps<{
	componentId: Component["id"];
	fieldKey: string;
}>();
const { componentId, fieldKey } = toRefs(props);
const component = computed(() => ss.getComponentById(componentId.value));

const rootEl: Ref<HTMLElement> = ref(null);
const assistedKeyEl: Ref<HTMLInputElement> = ref(null);
type Mode = "assisted" | "freehand";
const mode: Ref<Mode> = ref(null);
const assistedEntries: Ref<Record<string, string>> = ref({});
const formAdd: Ref<{ key: string; value: string }> = ref({
	key: "",
	value: "",
});

const setMode = async (newMode: Mode) => {
	if (mode.value == newMode) return;
	mode.value = newMode;

	if (mode.value == "assisted") {
		handleSwitchToAssisted();
	}

	await nextTick();
};

const handleSwitchToAssisted = () => {
	let currentValue = component.value.content[fieldKey.value];

	if (!currentValue) return;

	let parsedValue: any;

	// Attempt to populate assisted from existing JSON data

	try {
		parsedValue = JSON.parse(currentValue);
		if (typeof parsedValue != "object") {
			throw "Invalid structure.";
		}
		assistedEntries.value = parsedValue;
	} catch {
		component.value.content[fieldKey.value] = JSON.stringify(
			assistedEntries.value,
			null,
			2,
		);
	}
};

const addAssistedEntry = () => {
	const { key, value } = formAdd.value;
	if (key === "" || value === "") return;
	assistedEntries.value[key] = value;
	setContentValue(
		component.value.id,
		fieldKey.value,
		JSON.stringify(assistedEntries.value, null, 2),
	);
	formAdd.value = { key: "", value: "" };
	assistedKeyEl.value.focus();
};

const removeAssistedEntry = (key: string) => {
	delete assistedEntries.value[key];

	if (Object.keys(assistedEntries.value).length == 0) {
		setContentValue(component.value.id, fieldKey.value, undefined);
		return;
	}

	setContentValue(
		component.value.id,
		fieldKey.value,
		JSON.stringify(assistedEntries.value, null, 2),
	);
};

/**
 * Watcher for external mutations (like undo/redo).
 */
watch(
	() => component.value?.content[fieldKey.value],
	async (currentValue) => {
		if (!component.value) return;
		let parsedValue: any;

		try {
			parsedValue = JSON.parse(currentValue);
			assistedEntries.value = parsedValue;
		} catch {
			// If parsing fails, preserve the previous assistedEntries value
		}
	},
);

onMounted(async () => {
	const currentValue = component.value.content[fieldKey.value];
	let parsedValue: any;

	if (!currentValue) {
		setMode("assisted");
		return;
	}

	// Attempt assisted mode first, if the JSON can be parsed into an object

	try {
		parsedValue = JSON.parse(currentValue);
		if (typeof parsedValue != "object") {
			throw "Invalid structure.";
		}
		assistedEntries.value = parsedValue;
		setMode("assisted");
	} catch {
		// Fall back to freehand if assisted mode isn't possible
		setMode("freehand");
	}
});
</script>

<style scoped>
@import "./sharedStyles.css";

.chipStackContainer {
	padding: 12px;
	margin-top: 4px;
	padding-bottom: 12px;
	border-bottom: 1px solid var(--builderSeparatorColor);
}

.staticList {
	padding: 12px;
	border-bottom: 1px solid var(--builderSeparatorColor);
}

.staticList:empty::before {
	content: "No entries yet.";
}
.staticList .entry {
	display: flex;
	align-items: center;
	gap: 8px;
	width: 100%;
	max-width: 100%;
}

.staticList .entry div {
	overflow: hidden;
	padding-top: 4px;
	padding-bottom: 4px;
	flex: 1 1 auto;
}

.staticList .entry button {
	flex: 0 0 auto;
}

.formAdd {
	padding: 12px;
}

textarea {
	resize: vertical;
	height: 8em;
	padding: 12px;
}

input {
	margin-bottom: 8px;
}
</style>
