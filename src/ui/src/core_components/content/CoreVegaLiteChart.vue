<docs lang="md">
Generate a chart using Altair and pass it via state; it'll be converted to Vega-Lite specification.

\`state["my_chart"] = chart\`

Afterwards, you can reference the chart in the specification using the syntax \`@{my_chart}\`.

Alternatively, you can work with Vega-Lite directly.
</docs>

<template>
	<div ref="rootEl" class="CoreVegaLiteChart">
		<div ref="chartTargetEl" class="target"></div>
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const description = "A component that displays Vega-Lite/Altair charts.";

const defaultSpec = {
	$schema: "https://vega.github.io/schema/vega-lite/v5.json",
	description,
	data: {
		values: [
			{ a: "A", b: 100 },
			{ a: "B", b: 200 },
			{ a: "C", b: 150 },
			{ a: "D", b: 300 },
		],
	},
	mark: "bar",
	encoding: {
		x: { field: "a", type: "nominal" },
		y: { field: "b", type: "quantitative" },
	},
};

export default {
	streamsync: {
		name: "Vega Lite Chart",
		description,
		category: "Content",
		fields: {
			spec: {
				name: "Chart specification",
				default: JSON.stringify(defaultSpec, null, 2),
				desc: "Vega-Lite chart specification. Pass a Vega Altair chart using state or paste a JSON specification.",
				type: FieldType.Object,
			},
			cssClasses,
		},
	},
};
</script>

<script setup lang="ts">
import { inject, onMounted, Ref, ref, watch } from "vue";
import injectionKeys from "../../injectionKeys";

const rootEl: Ref<HTMLElement> = ref(null);
const chartTargetEl: Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);

const renderChart = async () => {
	if (import.meta.env.SSR) return;
	if (!fields.spec.value || !chartTargetEl.value) return;
	const { default: embed } = await import("vega-embed");
	await embed(chartTargetEl.value, fields.spec.value);
};

watch(
	() => fields.spec.value,
	(spec) => {
		if (!spec) return;
		renderChart();
	},
);

onMounted(() => {
	renderChart();
	new ResizeObserver(renderChart).observe(rootEl.value, {
		box: "border-box",
	});
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreVegaLiteChart {
	min-height: 1px;
}

.target {
	overflow: hidden;
}
</style>
