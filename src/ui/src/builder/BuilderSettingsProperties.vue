<template>
	<div
		v-if="ssbm.isSelectionActive() && fields"
		class="BuilderSettingsProperties"
	>
		<div class="sectionTitle">
			<span class="material-symbols-outlined"> tune </span>
			<h3>Properties</h3>
		</div>
		<div>
			<div
				v-for="propertyCategory in fieldCategories"
				:key="propertyCategory"
				class="propertyCategory"
			>
				<div
					v-if="fieldsByCategory[propertyCategory].length > 0"
					class="title"
				>
					<h4>{{ propertyCategory }}</h4>
				</div>
				<div
					v-for="[fieldKey, fieldValue] in fieldsByCategory[
						propertyCategory
					]"
					:key="fieldKey"
				>
					<div class="fieldWrapper">
						<div class="name">
							{{ fieldValue.name ?? fieldKey
							}}<span class="type"> : {{ fieldValue.type }}</span>
						</div>
						<BuilderFieldsColor
							v-if="fieldValue.type == FieldType.Color"
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
						></BuilderFieldsColor>

						<BuilderFieldsShadow
							v-if="fieldValue.type == FieldType.Shadow"
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
						></BuilderFieldsShadow>

						<BuilderFieldsKeyValue
							v-if="fieldValue.type == FieldType.KeyValue"
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
							:instance-path="selectedInstancePath"
						></BuilderFieldsKeyValue>

						<BuilderFieldsText
							v-if="fieldValue.type == FieldType.Text"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
						></BuilderFieldsText>

						<BuilderFieldsText
							v-if="fieldValue.type == FieldType.Number"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
						></BuilderFieldsText>

						<BuilderFieldsText
							v-if="fieldValue.type == FieldType.IdKey"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
						></BuilderFieldsText>

						<BuilderFieldsObject
							v-if="fieldValue.type == FieldType.Object"
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
						></BuilderFieldsObject>

						<BuilderFieldsWidth
							v-if="fieldValue.type == FieldType.Width"
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
						></BuilderFieldsWidth>

						<BuilderFieldsAlign
							v-if="fieldValue.type == FieldType.HAlign"
							class="content"
							direction="horizontal"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
						></BuilderFieldsAlign>

						<BuilderFieldsAlign
							v-if="fieldValue.type == FieldType.VAlign"
							class="content"
							direction="vertical"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
						></BuilderFieldsAlign>

						<BuilderFieldsPadding
							v-if="fieldValue.type == FieldType.Padding"
							class="content"
							:field-key="fieldKey"
							:component-id="selectedComponent.id"
						></BuilderFieldsPadding>

						<div v-if="fieldValue.desc" class="desc">
							{{ fieldValue.desc }}
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "../injectionKeys";
import { parseInstancePathString } from "../renderer/instancePath";
import { FieldCategory, FieldType, InstancePath } from "../writerTypes";
import BuilderFieldsAlign from "./BuilderFieldsAlign.vue";
import BuilderFieldsColor from "./BuilderFieldsColor.vue";
import BuilderFieldsKeyValue from "./BuilderFieldsKeyValue.vue";
import BuilderFieldsObject from "./BuilderFieldsObject.vue";
import BuilderFieldsPadding from "./BuilderFieldsPadding.vue";
import BuilderFieldsShadow from "./BuilderFieldsShadow.vue";
import BuilderFieldsText from "./BuilderFieldsText.vue";
import BuilderFieldsWidth from "./BuilderFieldsWidth.vue";

const wf = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const selectedInstancePath = computed<InstancePath>(() =>
	parseInstancePathString(ssbm.getSelection()?.instancePath),
);

const selectedComponent = computed(() => {
	return wf.getComponentById(ssbm.getSelectedId());
});

const fields = computed(() => {
	const { type } = selectedComponent.value;
	const definition = wf.getComponentDefinition(type);
	return definition.fields;
});

const fieldCategories = [FieldCategory.General, FieldCategory.Style];

const fieldsByCategory = computed(() => {
	const entries = Object.entries(fields.value);
	const result = {
		[FieldCategory.General]: entries.filter(
			([_, fieldValue]) =>
				!fieldValue.category ||
				fieldValue.category == FieldCategory.General,
		),
		[FieldCategory.Style]: entries.filter(
			([_, fieldValue]) => fieldValue.category == FieldCategory.Style,
		),
	};
	return result;
});
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSettingsProperties {
	padding: 24px;
}

.propertyCategory .title {
	margin-top: 24px;
}

textarea.content {
	resize: vertical;
	height: 8em;
}

input[type="color"].content {
	height: 48px;
}
</style>
