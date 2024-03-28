<template>
	<div class="ChildlessPlaceholder">
		<div class="content">
			<div class="title">
				<h2>Empty {{ definition.name }}</h2>
			</div>
			<div v-if="message" class="message">
				{{ message }}
			</div>
		</div>
	</div>
</template>
<script setup lang="ts">
import { computed, inject, toRefs } from "vue";
import { Component } from "../streamsyncTypes";
import injectionKeys from "../injectionKeys";

const ALLOWED_LIST_MAX_LENGTH = 10;
const ss = inject(injectionKeys.core);

interface Props {
	componentId: Component["id"];
}
const props = defineProps<Props>();
const { componentId } = toRefs(props);
const component = computed(() => ss.getComponentById(componentId.value));
const definition = computed(() =>
	ss.getComponentDefinition(component.value.type),
);

const typesToMessage = (
	types: Component["type"][],
	lastJoiner: "or" | "and",
) => {
	const definitions = types.map((type) => ss.getComponentDefinition(type));
	const names = definitions.map((def) => def?.name);
	const message = `${names.slice(0, -1).join(", ")} ${
		names.length > 1 ? lastJoiner : ""
	} ${names.at(-1)}`;
	return message;
};

const message = computed(() => {
	const containableTypes = ss.getContainableTypes(componentId.value);
	let message: string;

	if (containableTypes.length <= ALLOWED_LIST_MAX_LENGTH) {
		const typesMessage = typesToMessage(containableTypes, "and");
		message = `You can add ${typesMessage} components`;
	}

	return message;
});
</script>
<style scoped>
@import "./sharedStyles.css";

.ChildlessPlaceholder {
	background: rgba(0, 0, 0, 0.05);
	color: var(--primaryTextColor);
	padding: 16px;
	display: flex;
	align-items: center;
	justify-content: center;
	width: 100%;
	min-height: 100%;
}

.content {
	text-align: center;
}

.title > h2 {
	color: var(--primaryTextColor);
	opacity: 0.8;
}

.message {
	opacity: 0.5;
	margin-top: 8px;
}
</style>
