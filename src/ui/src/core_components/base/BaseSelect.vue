<template>
	<div
		:id="baseId"
		ref="rootEl"
		class="BaseSelect"
		tabindex="0"
		:data-mode="mode"
		:data-list-position="listPosition"
		role="listbox"
		:aria-activedescendant="
			highlightedOffset
				? `${baseId}-option-${highlightedOffset}`
				: undefined
		"
		@keydown="handleKeydown"
		@click="handleClick"
		@focusout="handleFocusOut"
	>
		<div ref="selectedOptionsEl" class="selectedOptions">
			<div v-show="selectedOptions.length == 0" class="placeholder">
				<template v-if="placeholder">{{ placeholder }}</template>
				<template v-else-if="mode == 'multiple' && maximumCount > 0"
					>Select up to {{ maximumCount }} option{{
						maximumCount > 1 ? "s" : ""
					}}...</template
				>
				<template v-else-if="mode == 'multiple'"
					>Select options....</template
				>
				<template v-else-if="mode == 'single'"
					>Select an option...</template
				>
			</div>
			<div
				v-for="optionKey in selectedOptions"
				:key="optionKey"
				class="option"
				:class="{ notFound: !options?.[optionKey] }"
				aria-selected="true"
			>
				<div v-if="options?.[optionKey]" class="desc" role="option">
					{{ options[optionKey] }}
				</div>
				<div v-else class="desc" role="option">
					{{ optionKey }}
				</div>

				<div
					class="remove"
					data-prevent-list="true"
					aria-label="Remove"
					@click="removeItem(optionKey)"
				>
					<i class="ri-close-line"></i>
				</div>
			</div>
			<input
				ref="inputEl"
				v-model="activeText"
				type="text"
				aria-autocomplete="none"
				tabindex="-1"
				@keydown="handleInputKeydown"
				@blur="handleInputBlur"
			/>
		</div>
		<div v-show="listPosition !== 'hidden'" ref="listEl" class="list">
			<div
				v-for="(option, optionKey, offset) in listOptions"
				:id="`${baseId}-option-${offset}`"
				:key="`${offset}-${optionKey}`"
				class="option"
				role="option"
				:data-list-offset="offset"
				data-prevent-list="true"
				:class="{ highlighted: highlightedOffset == offset }"
				@mousemove="highlightItem(offset)"
				@click="selectOption(optionKey)"
			>
				{{ option }}
			</div>
			<div v-if="Object.keys(listOptions).length == 0" class="empty">
				<template v-if="mode == 'multiple' && isMaximumCountReached"
					>Up to {{ maximumCount }} option{{
						maximumCount > 1 ? "s" : ""
					}}
					allowed.</template
				>
				<template v-else>No results</template>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, Ref, toRefs } from "vue";
import { nextTick } from "vue";
import { ref } from "vue";
import { watch } from "vue";

const emit = defineEmits(["change"]);

const props = defineProps<{
	baseId: string;
	activeValue: any;
	options: Record<string, string>;
	maximumCount: number;
	mode: "single" | "multiple";
	placeholder?: string;
}>();

const { baseId, activeValue, options, maximumCount, mode, placeholder } =
	toRefs(props);

const LIST_MAX_HEIGHT_PX = 200;
const rootEl: Ref<HTMLElement | null> = ref(null);
const inputEl: Ref<HTMLElement | null> = ref(null);
const selectedOptionsEl: Ref<HTMLElement | null> = ref(null);
const listEl: Ref<HTMLElement | null> = ref(null);
const activeText: Ref<string> = ref("");
const highlightedOffset: Ref<number | null> = ref(null);
const selectedOptions: Ref<string[]> = ref([]);
const listPosition: Ref<"top" | "bottom" | "hidden"> = ref("hidden");

const listOptions = computed(() => {
	if (mode.value == "multiple" && isMaximumCountReached.value) return {};
	const listed = {};
	Object.entries(options.value).forEach(([optionKey, option]) => {
		if (
			mode.value == "multiple" &&
			selectedOptions.value.includes(optionKey)
		)
			return;
		if (
			!option
				.toLocaleLowerCase()
				.includes(activeText.value.toLocaleLowerCase())
		)
			return;
		listed[optionKey] = option;
	});
	return listed;
});

const isMaximumCountReached = computed(() => {
	if (maximumCount.value <= 0) return false;
	if (selectedOptions.value.length < maximumCount.value) return false;
	return true;
});

watch(
	activeValue,
	() => {
		selectedOptions.value = [];

		activeValue.value.forEach?.((av: string) => {
			if (typeof options.value[av] === "undefined") return;
			selectedOptions.value.push(av);
		});
	},
	{ immediate: true },
);

watch(listOptions, () => {
	enforceHighlightBoundaries();
});

function enforceHighlightBoundaries() {
	if (highlightedOffset.value <= 0) {
		highlightedOffset.value = 0;
		return;
	}
	const maxOffset = Object.keys(listOptions.value).length - 1;
	if (highlightedOffset.value >= maxOffset) {
		highlightedOffset.value = maxOffset;
	}
}

watch(highlightedOffset, () => {
	if (highlightedOffset.value === null) return;
	const el = rootEl.value?.querySelector(
		`[data-list-offset="${highlightedOffset.value}"]`,
	);
	if (!el) return;
	el.scrollIntoView({ block: "nearest", inline: "nearest" });
});

function emitChangeEvent() {
	const optionKeys = Object.keys(options.value);
	const validSelectedOptions = selectedOptions.value.filter((o) =>
		optionKeys.includes(o),
	);
	emit("change", validSelectedOptions);
}

function removeItem(optionKey: string) {
	const index = selectedOptions.value.indexOf(optionKey);
	if (index !== -1) {
		selectedOptions.value.splice(index, 1);
		highlightedOffset.value = null;
	}
	emitChangeEvent();
}

function removeLastItem() {
	selectedOptions.value.pop();
	emitChangeEvent();
}

async function hideList(backToRoot = false) {
	listPosition.value = "hidden";
	activeText.value = "";
	if (!backToRoot) return;
	await nextTick();
	if (!rootEl.value) return;
	rootEl.value.tabIndex = 0;
	rootEl.value.focus();
}

function handleKeydown(ev: KeyboardEvent) {
	const key = ev.key;
	if (key == "Escape") {
		ev.preventDefault();
		hideList(true);
		return;
	}
	if (key !== "Tab" && key !== "Shift" && listPosition.value == "hidden") {
		showList();
		return;
	}
	if (key == "Enter") {
		if (highlightedOffset.value === null) return;
		const listKeys = Object.keys(listOptions.value);
		if (!listKeys || listKeys.length == 0) return;
		selectOption(listKeys[highlightedOffset.value]);
		return;
	}
	if (key == "ArrowUp") {
		ev.preventDefault();
		if (highlightedOffset.value === null) {
			const maxOffset = Object.keys(listOptions.value).length - 1;
			highlightedOffset.value = maxOffset;
			return;
		}
		highlightedOffset.value--;
		enforceHighlightBoundaries();
		return;
	}
	if (key == "ArrowDown") {
		ev.preventDefault();
		if (highlightedOffset.value === null) {
			highlightedOffset.value = 0;
			return;
		}
		highlightedOffset.value++;
		enforceHighlightBoundaries();
		return;
	}
}

function handleInputKeydown(ev: KeyboardEvent) {
	if (
		mode.value == "multiple" &&
		ev.key == "Backspace" &&
		!activeText.value
	) {
		removeLastItem();
	}
}

async function selectOption(optionKey: string) {
	if (mode.value == "single") {
		selectedOptions.value = [];
	} else {
		if (selectedOptions.value.includes(optionKey)) {
			return;
		}
	}
	selectedOptions.value.push(optionKey);
	emitChangeEvent();
	activeText.value = "";
	if (selectedOptions.value.length == maximumCount.value) {
		hideList(true);
	}
	await nextTick();
	selectedOptionsEl.value.scrollTop = selectedOptionsEl.value.scrollHeight;
}

function handleFocusOut(ev: FocusEvent) {
	const relatedEl = ev.relatedTarget as HTMLElement;
	if (!rootEl.value) return;
	if (rootEl.value.contains(relatedEl)) return;
	hideList(false);
}

function handleInputBlur(ev: FocusEvent) {
	const relatedEl = ev.relatedTarget as HTMLElement;
	if (!rootEl.value) return;
	if (rootEl.value.contains(relatedEl)) return;
	hideList(true);
}

function handleClick(ev: Event) {
	const el = ev.target as HTMLElement;
	if (el.dataset.preventList) return;
	showList();
}

async function showList() {
	if (listPosition.value !== "hidden") return;
	const { bottom: rootBottom } = rootEl.value.getBoundingClientRect();
	const bodyHeight = document.body.clientHeight;
	if (LIST_MAX_HEIGHT_PX + rootBottom >= bodyHeight) {
		listPosition.value = "top";
	} else {
		listPosition.value = "bottom";
	}
	await nextTick();
	rootEl.value.tabIndex = -1;
	inputEl.value?.focus();
}

function highlightItem(offset: number) {
	highlightedOffset.value = offset;
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";
.BaseSelect {
	width: 100%;
	position: relative;
	outline: none;
}

.selectedOptions {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
	padding: 8px;
	border: 1px solid var(--separatorColor);
	width: 100%;
	outline: none;
	min-height: 50px;
	background: var(--containerBackgroundColor);
	max-height: v-bind("`${LIST_MAX_HEIGHT_PX}px`");
	overflow-y: auto;
}

[data-mode]:not([data-list-position="hidden"]) .selectedOptions .placeholder {
	display: none;
}

[data-mode][data-list-position="hidden"] .selectedOptions .placeholder {
	display: flex;
	align-items: center;
	justify-content: center;
	padding-left: 8px;
	color: var(--secondaryTextColor);
}

.BaseSelect:focus-within[data-list-position="hidden"] .selectedOptions {
	border-color: var(--primaryTextColor);
}

[data-list-position="bottom"] .selectedOptions {
	border: 1px solid var(--primaryTextColor);
	border-bottom: 1px solid var(--containerBackgroundColor);
}

[data-list-position="top"] .selectedOptions {
	border: 1px solid var(--primaryTextColor);
	border-top: 1px solid var(--containerBackgroundColor);
}

.selectedOptions .option {
	background: var(--accentColor);
	color: var(--chipTextColor);
	border-radius: 4px;
	display: flex;
	gap: 4px;
	user-select: none;
	align-items: center;
	outline: none;
	min-height: 32px;
}

.selectedOptions .option.notFound {
	background: var(--separatorColor);
	color: var(--containerBackgroundColor);
}

[data-mode="single"]:not([data-list-position="hidden"])
	.selectedOptions
	.option {
	display: none;
}

.selectedOptions .option .desc {
	height: 100%;
	padding: 8px;
	display: flex;
	align-items: center;
}

[data-mode="multiple"] .selectedOptions .option .remove {
	display: flex;
	align-items: center;
	height: 100%;
	padding: 0 8px 0 8px;
	backdrop-filter: brightness(95%);
	cursor: pointer;
}

[data-mode="single"] .selectedOptions .option .remove {
	display: none;
}

.selectedOptions input {
	min-width: 120px;
	flex: 1 1 auto;
	border: none;
	border-bottom: 1px solid var(--separatorColor);
	transition: 0.2s ease-in-out border;
	display: none;
	color: var(--primaryTextColor);
	background: var(--containerBackgroundColor);
}

[data-mode]:not([data-list-position="hidden"]) .selectedOptions input {
	display: block;
}

.list {
	position: absolute;
	z-index: 10;
	background: var(--containerBackgroundColor);
	width: 100%;
	border: 1px solid var(--primaryTextColor);
	border-top: none;
	max-height: v-bind("`${LIST_MAX_HEIGHT_PX}px`");
	overflow-y: auto;
	overflow-x: hidden;
}

[data-list-position="top"] .list {
	box-shadow: 0 -4px 16px -4px rgba(0, 0, 0, 0.2);
	bottom: 100%;
	border: 1px solid var(--primaryTextColor);
	border-bottom: none;
}

[data-list-position="bottom"] .list {
	box-shadow: 0 4px 16px -4px rgba(0, 0, 0, 0.2);
	top: 100%;
	border: 1px solid var(--primaryTextColor);
	border-top: none;
}

.list .option {
	padding: 8px;
	overflow: hidden;
	white-space: nowrap;
	text-overflow: ellipsis;
	color: var(--primaryTextColor);
}

.list .option.highlighted {
	background: var(--selectedColor);
	padding: 8px;
}

.list .empty {
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: calc(v-bind("`${LIST_MAX_HEIGHT_PX}px`") / 2);
	padding-bottom: 8px;
	color: var(--secondaryTextColor);
}
</style>
