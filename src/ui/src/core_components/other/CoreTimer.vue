<template>
	<div
		ref="rootEl"
		class="CoreTimer"
		:class="{ failing: isFailing }"
		:style="rootStyle"
	></div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { accentColor, cssClasses } from "../../renderer/sharedStyleFields";
const description =
	"A component that emits an event repeatedly at specified time intervals, enabling time-based refresh.";

const ssTickHandlerStub = `
def handle_timer_tick(state):

	# Increment counter when the timer ticks

	state["counter"] += 1`.trim();

export default {
	streamsync: {
		name: "Timer",
		description,
		category: "Other",
		fields: {
			intervalMs: {
				name: "Interval (ms)",
				desc: "How much time to wait between ticks. A tick is considered finished when its event is handled.",
				default: "200",
				type: FieldType.Number,
			},
			isActive: {
				name: "Active",
				default: "yes",
				desc: "Whether the timer should trigger tick events.",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			accentColor,
			cssClasses,
		},
		events: {
			"ss-tick": {
				desc: "Emitted when the timer ticks.",
				stub: ssTickHandlerStub.trim(),
			},
		},
	},
};
</script>

<script setup lang="ts">
import { computed, inject, nextTick, onMounted, Ref, ref, watch } from "vue";
import injectionKeys from "../../injectionKeys";

const MIN_ANIMATION_RESET_MS = 500;
const MIN_ANIMATION_DURATION_MS = 1000;
const fields = inject(injectionKeys.evaluatedFields);
const ss = inject(injectionKeys.core);
const rootEl: Ref<HTMLElement> = ref(null);

const intervalMs = computed(() => fields.intervalMs.value);
const isActive = computed(() => fields.isActive.value == "yes");
const isFailing = ref(false);
const componentId = inject(injectionKeys.componentId);
const isTickHandlerSet = computed(
	() => !!ss.getComponentById(componentId)?.handlers?.["ss-tick"],
);

const rootStyle = computed(() => {
	const animationDurationMs = Math.max(
		intervalMs.value,
		MIN_ANIMATION_DURATION_MS,
	);
	return {
		"animation-duration": `${animationDurationMs}ms`,
	};
});

watch([isActive, intervalMs], () => {
	fireTimer();
});

watch(isTickHandlerSet, async (newIsTickHandlerSet) => {
	if (!newIsTickHandlerSet) return;
	await nextTick();
	fireTimer();
});

let animationTriggeredTime: number = 0;
let activeTimerId: number = null;

function clearActiveTimer() {
	clearTimeout(activeTimerId);
}

function fireTimer() {
	clearActiveTimer();

	if (!isActive.value || intervalMs.value < 0) return;
	if (!rootEl.value) return;

	if (Date.now() - animationTriggeredTime >= MIN_ANIMATION_RESET_MS) {
		rootEl.value.classList.remove("tick");
		rootEl.value.offsetWidth; // Forces a re-render
		animationTriggeredTime = Date.now();
		rootEl.value.classList.add("tick");
	}

	const callback = ({ ok }) => {
		isFailing.value = !ok;
		activeTimerId = setTimeout(() => {
			fireTimer();
		}, intervalMs.value);
	};
	const event = new CustomEvent("ss-tick", {
		detail: {
			callback,
		},
	});
	rootEl.value.dispatchEvent(event);
}
onMounted(() => {
	fireTimer();
});
</script>

<style scoped>
.CoreTimer {
	width: 12px;
	height: 12px;
	background: var(--accentColor);
	border-radius: 50%;
	filter: blur(1px);
}

.CoreTimer.failing {
	background: red;
}

.CoreTimer:not(.failing).tick {
	animation-name: tick;
}

@keyframes tick {
	0% {
		filter: blur(1px);
	}

	100% {
		filter: blur(3px);
	}
}
</style>
