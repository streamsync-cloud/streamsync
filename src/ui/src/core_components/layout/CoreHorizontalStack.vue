<template>
	<BaseContainer
		class="CoreHorizontalStack"
		:content-h-align="fields.contentHAlign.value"
		content-v-align="center"
		:content-padding="fields.contentPadding.value"
		:is-horizontal="true"
	>
		<slot></slot>
	</BaseContainer>
</template>

<script lang="ts">
import {
	contentHAlign,
	contentPadding,
	cssClasses,
} from "../../renderer/sharedStyleFields";

const description =
	"A layout component that stacks its child components horizontally, wrapping them to the next row if necessary.";

export default {
	streamsync: {
		name: "Horizontal Stack",
		description,
		allowedChildrenTypes: ["*"],
		category: "Layout",
		fields: {
			contentPadding: {
				...contentPadding,
				default: "0",
			},
			contentHAlign,
			cssClasses,
		},
	},
};
</script>
<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "../../injectionKeys";
import BaseContainer from "../base/BaseContainer.vue";

const fields = inject(injectionKeys.evaluatedFields);
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreHorizontalStack {
	width: 100%;
	flex-wrap: wrap;
}
</style>
