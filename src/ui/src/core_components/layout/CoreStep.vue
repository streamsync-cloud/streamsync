<template>
	<div
		v-show="
			stepContainerDirectChildInstanceItem?.instanceNumber ==
				STEP_BIT_INSTANCE_NUMBER ||
			(stepContainerDirectChildInstanceItem?.instanceNumber ==
				CONTENT_DISPLAYING_INSTANCE_NUMBER &&
				isStepActive)
		"
		class="CoreStep"
	>
		<button
			v-if="
				stepContainerDirectChildInstanceItem?.instanceNumber ==
				STEP_BIT_INSTANCE_NUMBER
			"
			class="bit"
			:disabled="!isBeingEdited"
			:class="{
				active: isStepActive,
				completed: fields.isCompleted.value == 'yes',
			}"
			stepindex="0"
			@click="activateStep"
		>
			<div class="indicator">
				<div class="linker left"></div>
				<div
					class="status"
					:class="{
						completed: fields.isCompleted.value == 'yes',
					}"
				>
					<i
						v-if="fields.isCompleted.value == 'yes'"
						class="ri-check-line"
					></i>
				</div>
				<div class="linker right"></div>
			</div>
			<div class="label">{{ fields.name.value }}</div>
		</button>
		<BaseContainer
			v-if="
				stepContainerDirectChildInstanceItem?.instanceNumber ==
				CONTENT_DISPLAYING_INSTANCE_NUMBER
			"
			v-show="isStepActive"
			class="container"
			:content-h-align="fields.contentHAlign.value"
			:content-padding="fields.contentPadding.value"
		>
			<slot></slot>
		</BaseContainer>
	</div>
</template>

<script lang="ts">
/**
 * This component follows a logic similar to the one seen in Tab and Tab Container.
 * Most of the complexity arises from allowing Repeater components between the Step Container (parent) and the Step (child).
 */

const STEP_BIT_INSTANCE_NUMBER = 0;
const CONTENT_DISPLAYING_INSTANCE_NUMBER = 1;

import { Component, FieldType, InstancePath } from "../../streamsyncTypes";
import { useEvaluator } from "../../renderer/useEvaluator";
import {
	contentHAlign,
	cssClasses,
	contentPadding,
} from "../../renderer/sharedStyleFields";
import { onBeforeUnmount } from "vue";

const description =
	"A container component that displays its child components as a step inside a Step Container.";

export default {
	streamsync: {
		name: "Step",
		description,
		allowedParentTypes: ["steps", "repeater"],
		allowedChildrenTypes: ["*"],
		category: "Layout",
		fields: {
			name: {
				name: "Name",
				default: "(No name)",
				init: "Step name",
				type: FieldType.Text,
			},
			contentPadding: {
				...contentPadding,
				default: "16px",
			},
			isCompleted: {
				name: "Completed",
				desc: "Use a state reference to dynamically mark this step as complete.",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			contentHAlign,
			cssClasses,
		},
		previewField: "name",
	},
};
</script>
<script setup lang="ts">
import { Ref, computed, inject, onBeforeMount, watch } from "vue";
import injectionKeys from "../../injectionKeys";
import BaseContainer from "./../base/BaseContainer.vue";
import { type StepsData } from "./CoreSteps.vue";

const fields = inject(injectionKeys.evaluatedFields);
const instancePath = inject(injectionKeys.instancePath);
const instanceData = inject(injectionKeys.instanceData);
const isBeingEdited = inject(injectionKeys.isBeingEdited);

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const componentId = inject(injectionKeys.componentId);
const { isComponentVisible } = useEvaluator(ss);
const selectedId = computed(() => ssbm?.getSelectedId());

const stepContainerData: Ref<StepsData> = getStepContainerData();

/**
 * Gets the negative index in the instancePath for the steps (Step Container) component
 * that governs this step.
 *
 * In line with Array.at(), -1 is the last element, -2 the previous in the chain.
 */
function getStepContainerNegativeIndex(): number {
	for (let i = -1; i > -1 * instancePath.length; i--) {
		const item = instancePath.at(i);
		const component = ss.getComponentById(item.componentId);
		if (!component) return;
		const type = component.type;
		if (type !== "steps") continue;
		return i;
	}
	return;
}

/**
 * Returns the InstanceData for the parent Step Container.
 */
function getStepContainerData(): Ref<StepsData> {
	const negativeIndex = getStepContainerNegativeIndex();
	if (typeof negativeIndex == "undefined") return;
	return instanceData.at(negativeIndex);
}

/**
 * Returns the InstancePath of the main instance (content-displaying) of this Step component.
 */
function getMatchingStepInstancePath() {
	const i = getStepContainerNegativeIndex() + 1; // Gets negative index for direct child of Step Container
	const itemsBefore = instancePath.slice(0, i);
	const itemsAfter = i + 1 < 0 ? instancePath.slice(i + 1) : [];
	const matchingInstancePath = [
		...itemsBefore,
		{
			componentId: instancePath.at(i).componentId,
			instanceNumber: CONTENT_DISPLAYING_INSTANCE_NUMBER,
		},
		...itemsAfter,
	];
	return matchingInstancePath;
}

/**
 * Activate this step (self-activate).
 */
function activateStep() {
	stepContainerData.value = {
		...stepContainerData.value,
		activeStep: getMatchingStepInstancePath(),
	};
}

/**
 * Activate the next step that hasn't been marked as completed.
 */
function activateNextStep() {
	const currentStepIndex = stepContainerData.value.steps.findIndex(
		(step) =>
			JSON.stringify(step.instancePath) == JSON.stringify(instancePath),
	);
	if (
		currentStepIndex == -1 ||
		currentStepIndex + 1 > stepContainerData.value.steps.length
	)
		return;
	const subsequentSteps = stepContainerData.value.steps.slice(
		currentStepIndex + 1,
	);
	let nextStep = subsequentSteps.find((step) => step.isCompleted != "yes");
	if (!nextStep) {
		const lastStep = stepContainerData.value.steps.at(-1);
		nextStep = lastStep;
	}
	stepContainerData.value = {
		...stepContainerData.value,
		activeStep: nextStep.instancePath,
	};
}

function checkIfStepIsParent(childId: Component["id"]): boolean {
	const child = ss.getComponentById(childId);
	if (!child || child.type == "root") return false;
	if (child.parentId == componentId) return true;
	return checkIfStepIsParent(child.parentId);
}

function activateDefaultStep() {
	if (fields.isCompleted.value != "yes") {
		activateStep();
		return;
	}
	activateNextStep();
}

const stepContainerDirectChildInstanceItem = computed(() => {
	const i = getStepContainerNegativeIndex() + 1;
	return instancePath.at(i);
});

/*
Activate the step if a component inside it was selected.
*/
watch(selectedId, (newSelectedId) => {
	if (!newSelectedId) return;
	if (!checkIfStepIsParent(newSelectedId)) return;
	activateStep();
});

/*
Determine whether this step is active by checking whether this step's InstancePath matches the 
active step's in the parent Step Container.
*/
const isStepActive = computed(() => {
	let contentDisplayingInstancePath: InstancePath;
	if (
		stepContainerDirectChildInstanceItem?.value.instanceNumber ==
		STEP_BIT_INSTANCE_NUMBER
	) {
		contentDisplayingInstancePath = getMatchingStepInstancePath();
	} else {
		contentDisplayingInstancePath = instancePath;
	}
	const activeStep = stepContainerData.value?.activeStep;
	return (
		JSON.stringify(activeStep) ==
		JSON.stringify(contentDisplayingInstancePath)
	);
});

/*
Prevent a step of being active while completed.
*/
watch([isStepActive, fields.isCompleted], () => {
	if (isBeingEdited.value) return;
	if (!isStepActive.value) return;
	if (fields.isCompleted.value == "yes") {
		activateNextStep();
	}
});

onBeforeMount(() => {
	if (
		stepContainerDirectChildInstanceItem?.value.instanceNumber ==
		STEP_BIT_INSTANCE_NUMBER
	)
		return;

	// Register steps in the Step Container

	if (
		typeof stepContainerData.value.steps.find(
			(step) => step.instancePath == instancePath,
		) === "undefined"
	) {
		stepContainerData.value.steps.push({
			instancePath,
			isCompleted: fields.isCompleted.value,
		});
	}

	const activeStep = stepContainerData.value?.activeStep;
	if (activeStep) return;
	if (!isComponentVisible(componentId, instancePath)) return;

	// During render of first step, mark the first non-completed step as active

	activateDefaultStep();
});

onBeforeUnmount(() => {
	const currentStepIndex = stepContainerData.value.steps.findIndex(
		(step) =>
			JSON.stringify(step.instancePath) == JSON.stringify(instancePath),
	);
	stepContainerData.value.steps.splice(currentStepIndex, 1);
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

button.bit {
	padding: 16px 0 0 0;
	border: none;
	border-radius: 0;
	margin: 0;
	display: flex;
	flex-direction: column;
	align-items: center;
	background: var(--containerBackgroundColor);
	color: var(--secondaryTextColor);
}

button.bit:disabled {
	cursor: auto;
}

button.bit:focus {
	color: var(--primaryTextColor);
}

button.bit.active,
button.bit.active:focus {
	color: var(--primaryTextColor);
}

.indicator {
	width: 100%;
	display: flex;
	gap: 4px;
	flex-direction: row;
	align-items: center;
}

.indicator .status {
	color: var(--primaryTextColor);
	display: flex;
	align-items: center;
	justify-content: center;
	height: 18px;
	width: 18px;
	border-radius: 50%;
	background: var(--containerBackgroundColor);
	border: 1px solid var(--separatorColor);
	outline: 4px solid var(--separatorColor);
	margin: 4px;
}

.bit.active .indicator .status {
	border: 2px solid var(--separatorColor);
	background: var(--accentColor);
	color: var(--containerBackgroundColor);
}

.bit:not(.active).completed .indicator .status {
	background: var(--separatorColor);
	border-color: transparent;
	color: var(--primaryTextColor);
}

.linker {
	height: 1px;
	background: var(--separatorColor);
	flex: 1 0 auto;
}

/* These declarations remove the lines before the first step and after the last step */

:not(.CoreRepeater) > .CoreStep:not(.beingEdited):first-child .linker.left {
	background: transparent;
}

:not(.CoreRepeater) > .CoreStep.beingEdited:nth-child(2) .linker.left {
	background: transparent;
}

:not(.CoreRepeater) > .CoreStep:not(.beingEdited):last-child .linker.right {
	background: transparent;
}

:not(.CoreRepeater) > .CoreStep.beingEdited:nth-last-child(2) .linker.right {
	background: transparent;
}

.label {
	padding: 8px 16px 0 16px;
}
</style>
