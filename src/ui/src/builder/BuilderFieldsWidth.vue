<template>
	<div ref="rootEl" class="BuilderFieldsWidth" tabindex="-1">
		<div class="chipStackContainer">
			<div class="chipStack">
				<button
					class="chip"
					tabindex="0"
					:class="{ active: mode == 'default' }"
					@click="
						() => {
							setMode('default');
							setContentValue(component.id, fieldKey, undefined);
						}
					"
				>
					Default
				</button>
				<button
					class="chip"
					tabindex="0"
					:class="{ active: mode == 'css' }"
					@click="setMode('css')"
				>
					CSS
				</button>
				<button
					class="chip"
					:class="{ active: mode == 'pick' }"
					tabindex="0"
					@click="setMode('pick')"
				>
					Pick
				</button>
			</div>
		</div>

		<div v-if="mode == 'pick' || mode == 'css'" class="main">
			<div v-if="mode == 'pick'" class="pickerContainer">
				<BuilderSelect
					:default-value="subMode"
					:options="selectOptions"
					@select="handleInputSelect"
				/>
				<div v-if="subMode == SubMode.fixed" class="fixedContainer">
					<input
						ref="fixedEl"
						type="text"
						:value="valuePickFixed"
						@input="handleInputFixed"
					/>
					<div>px</div>
				</div>
			</div>

			<input
				v-if="mode == 'css'"
				ref="freehandInputEl"
				type="text"
				:value="component.content[fieldKey]"
				@input="handleInputCss"
			/>
		</div>
	</div>
</template>

<script setup lang="ts">
import {
	computed,
	inject,
	nextTick,
	onBeforeUnmount,
	onMounted,
	Ref,
	ref,
	toRefs,
} from "vue";
import { Component } from "../streamsyncTypes";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";
import BuilderSelect from "./BuilderSelect.vue";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(ss, ssbm);

const rootEl: Ref<HTMLElement> = ref(null);
const pickerEl: Ref<HTMLInputElement> = ref(null);
const fixedEl: Ref<HTMLInputElement> = ref(null);
const freehandInputEl: Ref<HTMLInputElement> = ref(null);

type Mode = "pick" | "css" | "default";

enum SubMode {
	fixed = "fixed",
	fit_content = "fit-content",
	full = "full",
}

const subModes: Array<{
	key: SubMode;
	label: string;
	match: (v: string) => boolean;
	default: string;
	icon?: string;
}> = [
	{
		key: SubMode.fixed,
		label: "Fixed",
		match: (v) => v.endsWith("px"),
		default: "160px",
	},
	{
		key: SubMode.fit_content,
		label: "Fit Content",
		match: (v) => v == "fit-content",
		default: "fit-content",
	},
	{
		key: SubMode.full,
		label: "Full",
		match: (v) => v == "100%",
		default: "100%",
	},
];

const focusEls: Record<Mode, Ref<HTMLInputElement>> = {
	pick: pickerEl,
	css: freehandInputEl,
	default: null,
};

const props = defineProps<{
	componentId: Component["id"];
	fieldKey: string;
}>();

const { componentId, fieldKey } = toRefs(props);
const component = computed(() => ss.getComponentById(componentId.value));

const selectOptions = computed(() => {
	return subModes.map((m) => {
		return {
			value: m.key,
			label: m.label,
			icon: "ri-split-cells-horizontal",
		};
	});
});

const subMode = computed(() => {
	const value = component.value.content[fieldKey.value];
	for (const k in subModes) {
		if (value && subModes[k].match(value)) {
			return subModes[k].key;
		}
	}

	return null;
});

const valueCss = computed(() => {
	const value = component.value.content[fieldKey.value];
	if (!value) {
		return "";
	} else {
		return value;
	}
});

const valuePickFixed = computed(() => {
	const value = component.value.content[fieldKey.value];
	if (!value) {
		return null;
	} else if (value.endsWith("px")) {
		return value.substring(0, value.length - 2);
	}

	return null;
});

const getInitialMode = (): Mode => {
	if (!valueCss.value) {
		return "default";
	}

	for (const k in subModes) {
		if (subModes[k].match(valueCss.value)) {
			return "pick";
		}
	}

	return "css";
};

const mode: Ref<Mode> = ref(getInitialMode());

const autofocus = () => {
	const focusEl = focusEls[mode.value]?.value;
	if (!focusEl) return;
	focusEl.focus();

	if (typeof focusEl.selectionStart !== "number") return;
	focusEl.selectionStart = focusEl.selectionEnd = focusEl.value.length;
};

const setMode = async (newMode: Mode) => {
	if (mode.value == newMode) return;
	mode.value = newMode;
	await nextTick();
	autofocus();
};

const handleInputSelect = (select: string) => {
	for (const k in subModes) {
		if (subModes[k].key == select) {
			const value = subModes[k].default;
			component.value.content[fieldKey.value] = value;
			setContentValue(component.value.id, fieldKey.value, value);
		}
	}

	if (select == SubMode.fixed) {
		nextTick(() => {
			fixedEl.value.focus();
		});
	}
};

const handleInputCss = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
	);
};

const handleInputFixed = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value + "px",
	);
};

onMounted(() => {
	rootEl.value.addEventListener("focus", autofocus);
});

onBeforeUnmount(() => {
	rootEl.value.removeEventListener("focus", autofocus);
});
</script>

<style scoped>
@import "./sharedStyles.css";

.chipStackContainer {
	padding: 12px;
	margin-top: 4px;
	padding-bottom: 12px;
}
.main {
	border-top: 1px solid var(--builderSeparatorColor);
	padding: 12px;
}

.fixedContainer {
	display: flex;
	flex-direction: row;
	gap: 8px;
	padding: 8px;
}
</style>
