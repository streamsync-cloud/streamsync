<template>
	<div ref="rootEl" class="CoreRatingInput">
		<label v-if="fields.label.value">{{ fields.label.value }}</label>
		<div
			ref="unitsEl"
			class="units"
			:class="{ valueSet: feedbackRating !== null }"
			@click="handleClick"
			@mousemove="handleMousemove"
			@mouseout="handleMouseout"
		>
			<div
				v-for="n in [...Array(normalisedMaxValue).keys()]"
				:key="n"
				class="unit"
				:class="fields.feedback.value"
			>
				<div
					class="filler"
					:style="{
						width: `${
							feedbackRating > n
								? Math.min(feedbackRating - n, 1) * 100
								: 0
						}%`,
					}"
				></div>
				<div v-if="feedbackRating !== null" class="filler light"></div>
				<div v-if="fields.feedback.value == 'faces'" class="face">
					<svg viewBox="0 0 100 100">
						<circle class="eye left" cx="35" cy="38" r="6"></circle>
						<circle
							class="eye right"
							cx="65"
							cy="38"
							r="6"
						></circle>
						<path
							class="mouth"
							:d="getMouthPath(feedbackRating ?? n + 1)"
						></path>
					</svg>
				</div>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import {
	accentColor,
	cssClasses,
	primaryTextColor,
} from "../../renderer/sharedStyleFields";

const description =
	"A user input component that allows users to provide a rating.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

	# Set the state variable "rating" to the new value

	state["rating"] = payload`;

export default {
	streamsync: {
		name: "Rating Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			feedback: {
				name: "Feedback",
				default: "stars",
				type: FieldType.Text,
				options: {
					stars: "Stars",
					faces: "Faces",
					hearts: "Hearts",
				},
			},
			minValue: {
				name: "Minimum value",
				type: FieldType.Number,
				default: "1",
				desc: "Valid values are 0 and 1.",
			},
			maxValue: {
				name: "Max value",
				type: FieldType.Number,
				default: "5",
				desc: "Valid values are between 2 and 11.",
			},
			valueStep: {
				name: "Step",
				type: FieldType.Number,
				default: "1",
				desc: "Valid values are between 0.25 and 1.",
			},
			accentColor,
			primaryTextColor,
			cssClasses,
		},
		events: {
			"ss-number-change": {
				stub: onChangeHandlerStub,
				bindable: true,
			},
		},
	},
};
</script>

<script setup lang="ts">
import { Ref, computed, inject, ref } from "vue";
import injectionKeys from "../../injectionKeys";
import { useFormValueBroker } from "../../renderer/useFormValueBroker";

const fields = inject(injectionKeys.evaluatedFields);
const rootEl = ref(null);
const unitsEl: Ref<HTMLElement> = ref(null);
const ss = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);
const provisionalValue: Ref<number> = ref(null);

const { formValue, handleInput } = useFormValueBroker(ss, instancePath, rootEl);

function getRawRatingFromEvent(event: MouseEvent) {
	const evX = event.offsetX;
	const unitEls = unitsEl.value.querySelectorAll(".unit");
	let n = 0;
	unitEls.forEach((unitEl) => {
		const unitHtmlEl = unitEl as HTMLElement;
		if (evX > unitHtmlEl.offsetLeft + unitHtmlEl.offsetWidth) {
			n++;
		} else if (evX > unitHtmlEl.offsetLeft) {
			n += (evX - unitHtmlEl.offsetLeft) / unitHtmlEl.offsetWidth;
		}
	});
	return n;
}

function normaliseRawRating(n: number) {
	let nn =
		Math.ceil(n / normalisedStepValue.value) * normalisedStepValue.value;
	nn = Math.max(
		Math.min(nn, normalisedMaxValue.value),
		normalisedMinValue.value,
	);

	return nn;
}

function getRatingFromEvent(event: MouseEvent) {
	const rawRating = getRawRatingFromEvent(event);
	return normaliseRawRating(rawRating);
}

function handleMousemove(event: MouseEvent) {
	const n = getRatingFromEvent(event);
	provisionalValue.value = n;
}

function handleMouseout() {
	provisionalValue.value = null;
}

function getMouthPath(n: number) {
	const nn = Math.max(
		Math.min(n, normalisedMaxValue.value),
		normalisedMinValue.value,
	);
	const MIN_POINT = 45;
	const MAX_POINT = 95;
	const level =
		(nn - normalisedMinValue.value) /
		(normalisedMaxValue.value - normalisedMinValue.value);

	const mouthOffsetY = level * -10;
	const mouthY = 70 + mouthOffsetY;
	const guideY = MIN_POINT + level * (MAX_POINT - MIN_POINT) + mouthOffsetY;

	const d = `M30,${mouthY} Q50,${guideY} 70,${mouthY}`;
	return d;
}

function handleClick(event: MouseEvent) {
	const n = getRatingFromEvent(event);
	handleInput(n, "ss-number-change");
}

const normalisedMinValue = computed(() => {
	const MIN_VALUE_LOWER_LIMIT = 0;
	const MIN_VALUE_UPPER_LIMIT = 1;
	const minValue = Math.max(
		Math.min(fields.minValue.value, MIN_VALUE_UPPER_LIMIT),
		MIN_VALUE_LOWER_LIMIT,
	);
	return minValue;
});

const normalisedMaxValue = computed(() => {
	const MAX_VALUE_LOWER_LIMIT = 2;
	const MAX_VALUE_UPPER_LIMIT = 11;
	const maxValue = Math.max(
		Math.min(fields.maxValue.value, MAX_VALUE_UPPER_LIMIT),
		MAX_VALUE_LOWER_LIMIT,
	);
	return maxValue;
});

const normalisedStepValue = computed(() => {
	const STEP_VALUE_LOWER_LIMIT = 0.25;
	const STEP_VALUE_UPPER_LIMIT = 1;
	const step = Math.max(
		Math.min(fields.valueStep.value, STEP_VALUE_UPPER_LIMIT),
		STEP_VALUE_LOWER_LIMIT,
	);
	return step;
});

const feedbackRating = computed(() => {
	if (provisionalValue.value !== null) return provisionalValue.value;
	const formN = parseFloat(formValue.value);
	if (isNaN(formN)) return null;
	return formN;
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreRatingInput {
	width: fit-content;
}

label {
	display: block;
	margin-bottom: 8px;
	color: var(--primaryTextColor);
}

.units {
	margin-left: -8px;
	padding-left: 8px;
	padding-right: 8px;
	display: flex;
	gap: 8px;
	flex-wrap: nowrap;
	position: relative;
}

.unit {
	pointer-events: none;
	height: 28px;
	width: 28px;
	background: var(--separatorColor);
	overflow: hidden;
	position: relative;
}

.unit.stars {
	box-shadow: 0 0 8px 4px rgba(0, 0, 0, 0.2) inset;
	clip-path: polygon(
		50% 0%,
		61% 35%,
		98% 35%,
		68% 57%,
		79% 91%,
		50% 70%,
		21% 91%,
		32% 57%,
		2% 35%,
		39% 35%
	);
}

.unit.faces {
	box-shadow: 0 0 8px 0 rgba(0, 0, 0, 0.2) inset;
	clip-path: circle(50%);
}

.unit.hearts {
	box-shadow: 0 0 8px 0 rgba(0, 0, 0, 0.2) inset;
	clip-path: path(
		"M2.54139 14.2987C0.97724 12.7905 0 10.646 0 8.26667C0 3.70111 3.5983 0 8.03704 0C10.4025 0 12.5293 1.05112 14 2.72404C15.4707 1.05112 17.5975 0 19.963 0C24.4017 0 28 3.70111 28 8.26667C28 10.6181 27.0455 12.7402 25.5133 14.2455L14.0815 28L2.54139 14.2987Z"
	);
}

.unit .filler {
	position: absolute;
	top: 0;
	left: 0;
	width: 28px;
	height: 28px;
	background: var(--accentColor);
	box-shadow: none;
}

.unit .filler.light {
	opacity: 20%;
}

.unit .face {
	position: absolute;
	top: 0;
	left: 0;
	width: 28px;
	height: 28px;
	color: var(--primaryTextColor);
}

.valueSet .unit .face {
	color: var(--containerBackgroundColor);
}

.unit .face svg {
	width: 100%;
	height: 100%;
}

.unit .face .eye {
	fill: currentColor;
}

.unit .face .mouth {
	stroke: currentColor;
	fill: transparent;
	stroke-width: 5px;
}
</style>
