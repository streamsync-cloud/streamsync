<template>
	<div class="BuilderFieldsText" :data-key="props.fieldKey">
		<template
			v-if="
				!templateField.control ||
				templateField.control == FieldControl.Text
			"
		>
			<input
				type="text"
				:value="component.content[fieldKey]"
				class="content"
				autocorrect="off"
				autocomplete="off"
				spellcheck="false"
				:placeholder="templateField?.default"
				:list="
					templateField.options
						? `list-${componentId}-${fieldKey}`
						: undefined
				"
				@input="handleInput"
			/>
			<datalist
				v-if="templateField.options"
				:id="`list-${componentId}-${fieldKey}`"
			>
				<option
					v-for="(option, optionKey) in options"
					:key="optionKey"
					:value="optionKey"
				>
					<template
						v-if="option.toLowerCase() !== optionKey.toLowerCase()"
					>
						{{ option }}
					</template>
				</option>
			</datalist>
		</template>
		<template v-else-if="templateField.control == FieldControl.Textarea">
			<textarea
				v-capture-tabs
				class="content"
				:value="component.content[fieldKey]"
				:placeholder="templateField?.default"
				autocorrect="off"
				autocomplete="off"
				spellcheck="false"
				@input="handleInput"
			>
			</textarea>
		</template>
	</div>
</template>

<script setup lang="ts">
import { toRefs, inject, computed } from "vue";
import { Component, FieldControl } from "../streamsyncTypes";
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
const templateField = computed(() => {
	const { type } = component.value;
	const definition = ss.getComponentDefinition(type);
	return definition.fields[fieldKey.value];
});

const options = computed(() => {
	const field = templateField.value;
	if (field.options) {
		return typeof field.options === "function"
			? field.options(ss, componentId.value)
			: field.options;
	}
	return [];
});

const handleInput = (ev: Event) => {
	setContentValue(
		component.value.id,
		fieldKey.value,
		(ev.target as HTMLInputElement).value,
	);
};
</script>

<style scoped>
@import "./sharedStyles.css";

.content {
	padding: 16px 12px 12px 12px;
	width: 100%;
}

textarea {
	resize: vertical;
}
</style>
