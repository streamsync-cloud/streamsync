<docs lang="md">
You can listen to events triggered by Plotly.js and add interactivity to your charts.
For example, implement cross-filtering.
</docs>
<template>
	<div ref="rootEl" class="CorePlotlyGraph">
		<div ref="chartTargetEl" class="target"></div>
		<div class="mask" />
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const description = "A component that displays Plotly graphs.";

const defaultSpec = {
	data: [
		{
			x: ["a", "b", "c"],
			y: [22, 25, 29],
			type: "bar",
		},
	],
};

export default {
	streamsync: {
		name: "Plotly Graph",
		description,
		category: "Content",
		fields: {
			spec: {
				name: "Graph specification",
				default: JSON.stringify(defaultSpec, null, 2),
				desc: "Plotly graph specification. Pass it using state, e.g. @{fig}, or paste a JSON specification.",
				type: FieldType.Object,
			},
			cssClasses,
		},
		events: {
			"plotly-click": {
				desc: "Sends a list with the clicked points.",
			},
			"plotly-selected": {
				desc: "Sends a list with the selected points.",
			},
			"plotly-deselect": {
				desc: "Triggered when points are deselected.",
			},
		},
	},
};
</script>

<script setup lang="ts">
import { computed, inject, onMounted, Ref, ref, watch } from "vue";
import injectionKeys from "../../injectionKeys";

const rootEl: Ref<HTMLElement> = ref(null);
const chartTargetEl: Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);
const spec = computed(() => fields.spec.value);

const renderChart = async () => {
	if (import.meta.env.SSR) return;
	if (!spec.value || !chartTargetEl.value) return;
	const Plotly = await import("plotly.js-dist-min");
	if (!rootEl.value || rootEl.value.clientHeight == 0) return;
	Plotly.newPlot(chartTargetEl.value, spec.value);
	bindPlotlyEvents();
	if (spec.value?.layout?.autosize) {
		applyAutosize();
	}
};

function applyAutosize() {
	const parentEl = rootEl.value.parentElement;
	if (!parentEl?.clientHeight) return;
	rootEl.value.style.height = "100%";
	chartTargetEl.value.style.height = "100%";
}

function bindPlotlyEvents() {
	// Plotly extends HTMLElement and adds an "on" property

	chartTargetEl.value.on(
		"plotly_click",
		getPlotlyEventHandler("plotly-click"),
	);
	chartTargetEl.value.on(
		"plotly_selected",
		getPlotlyEventHandler("plotly-selected"),
	);
	chartTargetEl.value.on(
		"plotly_deselect",
		getPlotlyEventHandler("plotly-deselect"),
	);
}

function extractKeyInfoFromPoint(point: any) {
	return {
		curveNumber: point.curveNumber,
		pointNumber: point.pointNumber,
		pointNumbers: point.pointNumbers,
		x: point.x,
		y: point.y,
		z: point.z,
		label: point.label,
		lat: point.lat,
		lon: point.lon,
		xaxis: {
			anchor: point.xaxis?.anchor,
		},
		yaxis: {
			anchor: point.yaxis?.anchor,
		},
	};
}

function getPlotlyEventHandler(eventType: string) {
	return (plotlyEventData: any) => {
		const event = new CustomEvent(eventType, {
			detail: {
				payload: plotlyEventData?.points?.map((p: any) =>
					extractKeyInfoFromPoint(p),
				),
			},
		});
		rootEl.value.dispatchEvent(event);
	};
}

watch(spec, (newSpec) => {
	if (!newSpec) return;
	renderChart();
});

onMounted(async () => {
	await renderChart();
	if (!rootEl.value) return;
	new ResizeObserver(renderChart).observe(rootEl.value, {
		box: "border-box",
	});
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CorePlotlyGraph {
	position: relative;
	min-height: 1px;
}

.target {
	overflow: hidden;
}

.mask {
	pointer-events: none;
}

.beingEdited .mask {
	pointer-events: auto;
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0);
}

.beingEdited.selected .mask {
	pointer-events: none;
}
</style>
