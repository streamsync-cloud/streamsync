<template>
	<component :is="vnode" />
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { h, inject, watch, ref } from "vue";
import injectionKeys from "../../injectionKeys";

export default {
	streamsync: {
		name: "Reuse Component",
		description:
			"Those components are used to reuse other components. " +
			"Reused components share the same state and are updated together.",
		category: "Other",
		allowedChildrenTypes: [],
		fields: {
			proxyId: {
				name: "Component id",
				type: FieldType.Text,
				desc: "The id of the component to reuse.",
			},
		},
	},
};
</script>
<script setup lang="ts">
const fields = inject(injectionKeys.evaluatedFields);
const instancePath = inject(injectionKeys.instancePath);
const parentId = instancePath.at(-2).componentId;
const ss = inject(injectionKeys.core);
const renderProxiedComponent = inject(injectionKeys.renderProxiedComponent);
const isBeingEdited = inject(injectionKeys.isBeingEdited);
const componentId = inject(injectionKeys.componentId);
const vnode = ref(h("div", ""));
const proxyType = ss.getComponentById(parentId).type;
const parentType = ss.getComponentById(parentId).type;
const proxyDefinition = ss.getComponentDefinitionById(fields.proxyId);
const parentDef = ss.getComponentDefinitionById(parentId);

function renderError(message: string, cls: string) {
	vnode.value = h(
		"div",
		{ class: ["CoreReuse", cls] },
		isBeingEdited.value ? message : "",
	);
}

function isAllowedChildType(type) {
	return (
		parentDef.value.allowedChildrenTypes?.includes(type) ||
		parentDef.value.allowedChildrenTypes?.includes("*")
	);
}

function isAllowedParentType(type) {
	return (
		!proxyDefinition.value.allowedParentTypes ||
		proxyDefinition.value.allowedParentTypes?.includes(type)
	);
}

function render() {
	if (!fields.proxyId.value) {
		return renderError("No component selected to reuse", "empty");
	}
	if (componentId === fields.proxyId.value || !proxyDefinition.value) {
		return renderError(
			"The id specified for reuse doesn't match any component.",
			"invalid-value",
		);
	}

	if (!isAllowedChildType(proxyType) || !isAllowedParentType(parentType)) {
		return renderError(
			`The component cannot be reused here.`,
			"invalid-context",
		);
	}

	ss.setComponentDefinitionById(componentId, {
		slot: proxyDefinition.value.slot || "default",
		positionless: proxyDefinition.value.positionless || false,
	});
	const reusedNode = renderProxiedComponent(fields.proxyId.value, 0, {
		class: ["CoreReuse"],
	});
	vnode.value = reusedNode;
}

watch([fields.proxyId, proxyDefinition], render, { immediate: true });
</script>
