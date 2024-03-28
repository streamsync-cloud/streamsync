<template>
	<div ref="rootEl" class="BuilderFieldsPadding" tabindex="-1">
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
				<div v-if="subMode == SubMode.all_sides" class="row">
					<i class="ico ico-padding-4-side"></i>
					<input
						ref="fixedEl"
						type="text"
						:value="valuePadding[0]"
						@input="handleInputs($event, subMode)"
					/>
					<div>px</div>
				</div>
				<div v-if="subMode == SubMode.xy_sides">
					<div class="row">
						<i class="ico ico-padding-x-side"></i>
						<input
							ref="fixedEl"
							type="text"
							:value="valuePadding[0]"
							@input="handleInputs($event, subMode, 'x')"
						/>
						<div>px</div>
					</div>
					<div class="row">
						<i class="ico ico-padding-y-side"></i>
						<input
							type="text"
							:value="valuePadding[2]"
							@input="handleInputs($event, subMode, 'y')"
						/>
						<div>px</div>
					</div>
				</div>
				<div v-if="subMode == SubMode.per_side">
					<div class="row">
						<i class="ico ico-padding-left-side"></i>
						<input
							ref="fixedEl"
							type="text"
							:value="valuePadding[0]"
							@input="handleInputs($event, subMode, 'left')"
						/>
						<div>px</div>
					</div>
					<div class="row">
						<i class="ico ico-padding-right-side"></i>
						<input
							type="text"
							:value="valuePadding[1]"
							@input="handleInputs($event, subMode, 'right')"
						/>
						<div>px</div>
					</div>
					<div class="row">
						<i class="ico ico-padding-top-side"></i>
						<input
							type="text"
							:value="valuePadding[2]"
							@input="handleInputs($event, subMode, 'top')"
						/>
						<div>px</div>
					</div>
					<div class="row">
						<i class="ico ico-padding-bottom-side"></i>
						<input
							type="text"
							:value="valuePadding[3]"
							@input="handleInputs($event, subMode, 'bottom')"
						/>
						<div>px</div>
					</div>
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
import { languages } from "monaco-editor";
import css = languages.css;

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const { setContentValue } = useComponentActions(ss, ssbm);

const rootEl: Ref<HTMLElement> = ref(null);
const pickerEl: Ref<HTMLInputElement> = ref(null);
const fixedEl: Ref<HTMLInputElement> = ref(null);
const freehandInputEl: Ref<HTMLInputElement> = ref(null);

type Mode = "pick" | "css" | "default";

enum SubMode {
	all_sides = "all_sides",
	xy_sides = "XY sides",
	per_side = "Per side",
}

const subModes: Array<{
	key: SubMode;
	label: string;
	match: (v: string) => boolean;
	default: () => string;
	icon?: string;
}> = [
	{
		key: SubMode.all_sides,
		label: "All sides",
		match: (v) => v.split(" ").length == 1 && v.endsWith("px"),
		default: () => (rawPadding.value ? rawPadding.value[0] : "0px"),
	},
	{
		key: SubMode.xy_sides,
		label: "XY sides",
		match: (v) => v.split(" ").length == 2 && v.endsWith("px"),
		default: () =>
			rawPadding.value
				? rawPadding.value[2] + " " + rawPadding.value[0]
				: "0px 0px",
	},
	{
		key: SubMode.per_side,
		label: "Per side",
		match: (v) => v.split(" ").length == 4 && v.endsWith("px"),
		default: () =>
			rawPadding.value
				? [
						rawPadding.value[3],
						rawPadding.value[1],
						rawPadding.value[2],
						rawPadding.value[0],
					].join(" ")
				: "0px 0px 0px 0px",
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
		return { value: m.key, label: m.label, icon: "ico ico-padding-4-side" };
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

const valuePadding = computed(() => {
	const values = rawPadding.value;
	if (!values) {
		return ["0", "0", "0", "0"];
	} else {
		return [
			values[0].substring(0, values[0].length - 2),
			values[1].substring(0, values[1].length - 2),
			values[2].substring(0, values[2].length - 2),
			values[3].substring(0, values[3].length - 2),
		];
	}
});

/**
 * Returns the padding value as an array of 4 values, or null if the value is not valid
 */
const rawPadding = computed(() => {
	const value = component.value.content[fieldKey.value];
	if (!value) {
		return null;
	} else {
		const values = value.split(" ");
		if (values.length == 1 && values[0].endsWith("px")) {
			return [values[0], values[0], values[0], values[0]];
		} else if (
			values.length == 2 &&
			values[0].endsWith("px") &&
			values[0].endsWith("px")
		) {
			return [values[1], values[1], values[0], values[0]];
		} else if (
			values.length == 4 &&
			values[0].endsWith("px") &&
			values[1].endsWith("px") &&
			values[2].endsWith("px") &&
			values[3].endsWith("px")
		) {
			return [values[3], values[1], values[0], values[2]];
		}
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
			const value = subModes[k].default();
			component.value.content[fieldKey.value] = value;
			setContentValue(component.value.id, fieldKey.value, value);
		}
	}

	nextTick(() => {
		fixedEl.value.focus();
	});
};

const handleInputCss = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
	);
};

const handleInputs = (ev: Event, subMode: SubMode, inputType?: string) => {
	const value = (ev.target as HTMLInputElement).value;
	const cssValue = component.value.content[fieldKey.value];

	if (subMode == SubMode.all_sides) {
		setContentValue(component.value.id, fieldKey.value, value + "px");
	} else if (subMode == SubMode.xy_sides) {
		const partCssValues = cssValue.split(" ");
		if (inputType == "x") {
			partCssValues[1] = value + "px";
		} else if (inputType == "y") {
			partCssValues[0] = value + "px";
		}

		setContentValue(
			component.value.id,
			fieldKey.value,
			partCssValues.join(" "),
		);
	} else if (subMode == SubMode.per_side) {
		const partCssValues = cssValue.split(" ");
		if (inputType == "top") {
			partCssValues[0] = value + "px";
		} else if (inputType == "right") {
			partCssValues[1] = value + "px";
		} else if (inputType == "bottom") {
			partCssValues[2] = value + "px";
		} else if (inputType == "left") {
			partCssValues[3] = value + "px";
		}

		setContentValue(
			component.value.id,
			fieldKey.value,
			partCssValues.join(" "),
		);
	}
};

const handleInputXYsides = (ev: Event) => {
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
@import "./ico.css";

.chipStackContainer {
	padding: 12px;
	margin-top: 4px;
	padding-bottom: 12px;
}

.main {
	border-top: 1px solid var(--builderSeparatorColor);
	padding: 12px;
}

.row {
	display: flex;
	flex-direction: row;
	gap: 8px;
	padding: 8px;
	align-items: center;
}

.row input {
	width: calc(100% - 32px) !important;
}
</style>
