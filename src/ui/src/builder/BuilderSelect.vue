Usage: ```js // icon is using https://remixicon.com const options = [ { value:
"auto", label: "Default" }, { value: "fit-content", label: "Fit content", icon:
"ri-split-cells-horizontal" }, ]; const select = (value: string) => {
console.log(value); }; ``` ```
<BuilderSelect :options="options" @select="select" />
``` ```
<BuilderSelect :options="options" defaultValue="fit-content" @select="select" />
``` You can specify a default icon from https://remixicon.com ```
<BuilderSelect
	:options="options"
	defaultValue="fit-content"
	defaultIcon="ri-expand-up-down-fill"
	@select="select"
/>
```

<template>
	<!-- inspired from https://andrejgajdos.com/custom-select-dropdown -->
	<div class="selectWrapper" @click="open">
		<div ref="selectEl" class="select">
			<div class="selectTrigger">
				<div class="selectContent">
					<div v-if="currentLabel != null" class="flexRow">
						<div><i :class="currentIcon"></i></div>
						<div>{{ currentLabel }}</div>
					</div>
				</div>
				<div class="selectArrow">
					<i class="ri-arrow-down-s-fill"></i>
				</div>
			</div>
			<div class="selectOptions">
				<div
					v-for="option in compOptions"
					:key="option.value"
					class="selectOption"
					:data-value="option.value"
					:class="option.class"
					@click="select"
				>
					<div class="flexRow">
						<div><i :class="option.icon"></i></div>
						<div>{{ option.label }}</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, ref, Ref } from "vue";

const selectEl: Ref<HTMLElement> = ref(null);

const props = defineProps<{
	options?: Array<{ value: string; label: string; icon?: string }>;
	defaultValue?: string;
	defaultIcon?: string;
}>();

let currentValue = ref(props.defaultValue);

const currentLabel = computed(() => {
	const option = props.options.find(
		(option) => option.value == currentValue.value,
	);
	return option ? option.label : "";
});

const currentIcon = computed(() => {
	const defaultIcon = props.defaultIcon ? props.defaultIcon : "ri-empty";
	const option = props.options.find(
		(option) => option.value == currentValue.value,
	);
	return option && option.icon ? option.icon : defaultIcon;
});

const emit = defineEmits(["select"]);

let compOptions = computed(() => {
	const options_list = props.options.map((option) => {
		let new_option = { ...option, class: "" };
		if (new_option.value == currentValue.value) {
			new_option.class = "selected";
			new_option.icon = new_option.icon ? new_option.icon : "ri-empty";
		} else {
			new_option.class = "";
			new_option.icon = new_option.icon ? new_option.icon : "ri-empty";
		}
		return new_option;
	});

	return options_list;
});

const open = () => {
	selectEl.value.classList.toggle("open");
};

const select = (event) => {
	const value = event.currentTarget.getAttribute("data-value");
	currentValue.value = value;
	emit("select", value);
};
</script>

<style scoped>
@import "./ico.css";

.selectWrapper {
	position: relative;
	user-select: none;
	width: 100%;
}

.select {
	position: relative;
	display: flex;
	flex-direction: column;
}

.selectTrigger {
	position: relative;
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 8px;
	font-weight: 400;
	color: #3b3b3b;
	height: 32px;
	background: #ffffff;
	cursor: pointer;
}

.selectOptions {
	position: absolute;
	display: block;
	top: 100%;
	left: 0;
	right: 0;
	border: 1px solid #394a6d;
	background: #fff;
	transition: all 0.2s;
	opacity: 0;
	visibility: hidden;
	pointer-events: none;
	z-index: 2;
}

.select.open .selectOptions {
	opacity: 1;
	visibility: visible;
	pointer-events: all;
}

.selectOption {
	position: relative;
	display: block;
	padding: 8px;
	font-weight: 400;
	color: #000000e6;
	cursor: pointer;
	transition: all 0.2s;
}

.selectOption:hover {
	cursor: pointer;
	background-color: #000000b3;
	color: #fff;
}

.selected {
	background-color: #000000b3;
	color: #fff;
}

.selectArrow {
	position: relative;
	display: flex;
	align-items: center;
	justify-content: space-between;
	font-weight: 300;
	color: #000000e6;
}

.flexRow {
	display: flex;
	flex-direction: row;
	gap: 8px;
}

.ri-empty {
	display: block;
	width: 12px;
}
</style>
