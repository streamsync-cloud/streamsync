<template>
	<div class="CoreSteps">
		<nav
			class="stepSelector horizontal"
			data-streamsync-cage
			data-streamsync-container
		>
			<slot :instance-number="0"></slot>
		</nav>
		<div class="container">
			<slot :instance-number="1"></slot>
		</div>
	</div>
</template>

<script lang="ts">
import {
	accentColor,
	primaryTextColor,
	secondaryTextColor,
	containerBackgroundColor,
	containerShadow,
	separatorColor,
	buttonColor,
	buttonTextColor,
	buttonShadow,
	cssClasses,
} from "../../renderer/sharedStyleFields";

const description =
	"A container component for displaying Step components, allowing you to implement a stepped workflow.";

export default {
	streamsync: {
		name: "Step Container",
		description,
		category: "Layout",
		allowedChildrenTypes: ["step", "repeater"],
		fields: {
			accentColor,
			primaryTextColor,
			secondaryTextColor,
			containerBackgroundColor,
			containerShadow,
			separatorColor,
			buttonColor,
			buttonTextColor,
			buttonShadow,
			cssClasses,
		},
	},
};
</script>
<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "../../injectionKeys";
import { InstancePath } from "../../streamsyncTypes";

export type StepsData = {
	activeStep: InstancePath;
	steps: {
		instancePath: InstancePath;
		isCompleted: string;
	}[];
};

const instanceData = inject(injectionKeys.instanceData);

const stepsData: StepsData = {
	activeStep: undefined,
	steps: [],
};

instanceData.at(-1).value = stepsData;
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreSteps {
	width: 100%;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	background: var(--containerBackgroundColor);
	overflow: hidden;
}

.stepSelector {
	pointer-events: all;
	display: flex;
	gap: 0;
	color: var(--secondaryTextColor);
	padding: 0 16px 0 16px;
	max-width: 100%;
	overflow-x: auto;
	justify-content: center;
}

.childless > .stepSelector {
	display: none;
}

.container {
	background: var(--containerBackgroundColor);
	box-shadow: var(--containerShadow);
}

.childless > .container {
	border: none;
}
</style>
