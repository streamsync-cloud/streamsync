<template>
	<div ref="rootEl" class="BuilderFieldsAlign" tabindex="-1">
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
	ComputedRef,
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
const freehandInputEl: Ref<HTMLInputElement> = ref(null);

type Mode = "pick" | "css" | "default";

enum SubMode {
	hleft = "start",
	hcenter = "center",
	hright = "end",
	// eslint-disable-next-line @typescript-eslint/no-duplicate-enum-values
	vtop = "start",
	// eslint-disable-next-line @typescript-eslint/no-duplicate-enum-values
	vcenter = "center",
	// eslint-disable-next-line @typescript-eslint/no-duplicate-enum-values
	vbottom = "end",
}

type SubModes = {
	key: SubMode;
	label: string;
	match: (v: string) => boolean;
	default: string;
	icon?: string;
}[];

const horizontalSubmodes: SubModes = [
	{
		key: SubMode.hleft,
		label: "Left",
		match: (v) => v == "start",
		default: "start",
		icon: "ri-align-left",
	},
	{
		key: SubMode.hcenter,
		label: "Center",
		match: (v) => v == "center",
		default: "center",
		icon: "ri-align-center",
	},
	{
		key: SubMode.hright,
		label: "Right",
		match: (v) => v == "end",
		default: "end",
		icon: "ri-align-right",
	},
];

const verticalSubmodes: SubModes = [
	{
		key: SubMode.vtop,
		label: "Top",
		match: (v) => v == "start",
		default: "start",
		icon: "ri-align-top",
	},
	{
		key: SubMode.vcenter,
		label: "Center",
		match: (v) => v == "center",
		default: "center",
		icon: "ri-align-vertically",
	},
	{
		key: SubMode.vbottom,
		label: "Bottom",
		match: (v) => v == "end",
		default: "end",
		icon: "ri-align-bottom",
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
	direction: "horizontal" | "vertical";
}>();

const { componentId, fieldKey, direction } = toRefs(props);
const component = computed(() => ss.getComponentById(componentId.value));

const subModes: ComputedRef<SubModes> = computed(() => {
	if (direction.value == "vertical") return verticalSubmodes;
	if (direction.value == "horizontal") return horizontalSubmodes;
	return verticalSubmodes;
});

const selectOptions = computed(() => {
	return subModes.value.map((m) => {
		return { value: m.key, label: m.label, icon: m.icon };
	});
});

const subMode = computed(() => {
	const value = component.value.content[fieldKey.value];
	for (const k in subModes.value) {
		if (value && subModes.value[k].match(value)) {
			return subModes.value[k].key;
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

const getInitialMode = (): Mode => {
	if (!valueCss.value) {
		return "default";
	}

	for (const k in subModes.value) {
		if (subModes.value[k].match(valueCss.value)) {
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
	for (const k in subModes.value) {
		if (subModes.value[k].key == select) {
			const value = subModes.value[k].default;
			component.value.content[fieldKey.value] = value;
			setContentValue(component.value.id, fieldKey.value, value);
		}
	}
};

const handleInputCss = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
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
</style>
