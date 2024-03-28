<template>
	<div ref="rootEl" class="CorePDF">
		<div v-if="fields.controls.value === 'yes'" class="controls">
			<button @click="() => gotoPage(page - 1)">
				<i class="ri-arrow-up-s-line" />
			</button>
			<button @click="() => gotoPage(page + 1)">
				<i class="ri-arrow-down-s-line" />
			</button>
			<span :key="page">{{ page }} / {{ pages }}</span>
			<button :disabled="loading" @click="incrementScale">
				<i class="ri-zoom-in-line" />
			</button>
			<button :disabled="loading" @click="decrementScale">
				<i class="ri-zoom-out-line" />
			</button>
			<span>{{ Math.round(scale * 100) }}%</span>
			<span class="separator" />
			<button v-if="matches.length" @click="decrementMatchIdx">
				<i class="ri-arrow-up-s-line" />
			</button>
			<button v-if="matches.length" @click="incrementMatchIdx">
				<i class="ri-arrow-down-s-line" />
			</button>
			<span v-if="matches.length"
				>Matches {{ currentMatch }} / {{ matches.length }}</span
			>
		</div>
		<div ref="viewerEl" class="viewer" @scroll="scroll">
			<div v-for="p in pages" :key="p" :page="p" class="page">
				<VuePDF
					:scale="scale"
					:pdf="pdf"
					:page="p"
					text-layer
					:highlight-text="highlightText"
					:highlight-options="highlightOptions"
					@highlight="(e) => onHighlight(e)"
					@loaded="onLoaded"
				/>
			</div>
		</div>
		<div class="mask" />
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import {
	cssClasses,
	separatorColor,
	primaryTextColor,
	containerBackgroundColor,
} from "../../renderer/sharedStyleFields";

const description = "A component to embed PDF documents.";

export default {
	streamsync: {
		name: "PDF",
		description,
		category: "Embed",
		fields: {
			source: {
				name: "PDF source",
				type: FieldType.Text,
				desc: "A valid URL. Alternatively, you can provide a state reference to a packed PDF file.",
			},
			highlights: {
				name: "Highlights",
				default: JSON.stringify([]),
				desc: "A list of highlights to be applied to the PDF as a JSON array of strings.",
				type: FieldType.Object,
			},
			selectedMatch: {
				name: "Selected highlight match",
				default: null,
				desc: "The index of the selected highlight match.",
				type: FieldType.Number,
			},
			page: {
				name: "Page",
				type: FieldType.Number,
				desc: "The page to be displayed.",
			},
			controls: {
				name: "Controls",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
				desc: "Show controls to navigate the PDF.",
				default: "yes",
			},
			containerBackgroundColor,
			separatorColor,
			primaryTextColor,
			cssClasses,
		},
	},
};
</script>

<script setup lang="ts">
import { inject, ref, watch, computed, onMounted } from "vue";
import injectionKeys from "../../injectionKeys";
import "@tato30/vue-pdf/style.css";

type MatchType = { str: string; page: number; index: number };

const fields = inject(injectionKeys.evaluatedFields);

let pdf, pages, VuePDF;

const highlightText = computed(() => {
	return fields.highlights.value
		? fields.highlights.value
				.map((v: string) => v.replaceAll("|", "\\|"))
				.join("|")
		: "";
});
const highlightOptions = ref({
	completeWords: false,
	ignoreCase: true,
});
const scale = ref(1);
const page = ref(1);
const matches = ref<MatchType[]>([]);
const currentMatch = ref(0);
const rootEl = ref(null);
const viewerEl = ref(null);
const loading = ref(false);

const pagesLoaded = ref(0);
const highlightsList = ref([]);

onMounted(async () => {
	if (import.meta.env.SSR) return;
	const VuePDFLib = await import("@tato30/vue-pdf");
	VuePDF = VuePDFLib.VuePDF;
	const usePDF = VuePDFLib.usePDF;
	({ pdf, pages } = usePDF(fields.source));
	reload();
});

const reload = () => {
	loading.value = true;
	pagesLoaded.value = 0;
	highlightsList.value = [];
	matches.value = [];
};

const onHighlight = (value) => {
	highlightsList.value = [...highlightsList.value, value].sort((a, b) => {
		return a.page - b.page;
	});
};

const onLoaded = (e) => {
	pagesLoaded.value++;
};

const buildMatches = () => {
	matches.value = highlightsList.value
		.reduce(
			(acc, item) => [
				...acc,
				...item.matches.map((m: MatchType, idx: number) => ({
					page: item.page,
					str: m.str,
					index: idx,
				})),
			],
			[],
		)
		.sort((a, b) => {
			if (a.page === b.page) {
				return a.index - b.index;
			}
			return a.page - b.page;
		});
};

const renderingComplete = () => {
	buildMatches();
	if (currentMatch.value) {
		gotoHighlight(currentMatch.value);
	}
	if (fields.selectedMatch.value) {
		currentMatch.value = fields.selectedMatch.value;
	}
};

const scroll = (event) => {
	const c = event.target.getBoundingClientRect();
	const r = [...event.target.children]
		.filter((child) => child.className.includes("page"))
		.find((child) => {
			const e = child.getBoundingClientRect();
			const relativeY = e.y - c.y;
			return (
				relativeY < c.height / 2 && relativeY + e.height > c.height / 2
			);
		});
	if (r) {
		page.value = Number(r.getAttribute("page"));
	}
};

const calcScrollPosition = (targetEl: HTMLElement, parentEl: HTMLElement) => {
	let offsetTop = 0;
	let el = targetEl;
	while (el && el !== parentEl) {
		offsetTop += el.offsetTop;
		el = el.offsetParent as HTMLElement;
	}
	return offsetTop;
};

const gotoHighlight = (matchIdx: number) => {
	if (matchIdx < 1 || matchIdx > matches.value.length) {
		return;
	}
	const match = matches.value[matchIdx - 1];
	if (!match) return;
	const matchEls = rootEl.value.querySelectorAll(
		`div[page='${match.page}'] span.highlight`,
	);
	const matchEl = matchEls[match.index];
	// scrollIntoView is breaking pdf viewer
	viewerEl.value.scrollTop = calcScrollPosition(matchEl, viewerEl.value);
};

const gotoPage = (page: number) => {
	if (page < 1 || page > pages.value) {
		return;
	}
	const pageEl = rootEl.value.querySelector("div[page='" + page + "']");
	viewerEl.value.scrollTop = calcScrollPosition(pageEl, viewerEl.value);
};

const incrementMatchIdx = () => {
	if (currentMatch.value < matches.value.length) {
		currentMatch.value = currentMatch.value + 1;
	} else {
		currentMatch.value = 1;
	}
};

const decrementMatchIdx = () => {
	if (currentMatch.value > 1) {
		currentMatch.value = currentMatch.value - 1;
	} else {
		currentMatch.value = matches.value.length;
	}
};

const incrementScale = () => {
	scale.value = scale.value < 2 ? scale.value + 0.1 : scale.value;
};

const decrementScale = () => {
	scale.value = scale.value > 0.25 ? scale.value - 0.1 : scale.value;
};

watch(pagesLoaded, () => {
	if (pagesLoaded.value === pages.value) {
		if (fields.page.value) {
			gotoPage(fields.page.value);
		}
	}
});

watch([highlightsList, pagesLoaded], () => {
	if (
		(!highlightText.value || highlightsList.value.length === pages.value) &&
		pagesLoaded.value === pages.value
	) {
		renderingComplete();
		loading.value = false;
	}
});

watch(scale, () => {
	reload();
});

watch(fields.source, () => {
	reload();
});

watch(fields.highlights, () => {
	highlightsList.value = [];
	matches.value = [];
});

watch(currentMatch, () => {
	gotoHighlight(currentMatch.value);
});

watch(fields.selectedMatch, () => {
	currentMatch.value = fields.selectedMatch.value;
});

watch(fields.page, () => {
	gotoPage(fields.page.value);
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CorePDF {
	position: relative;
	display: flex;
	flex-direction: column;
	width: 100%;
	height: 80vh;
	color: var(--primaryTextColor);
}

.CorePDF .controls {
	flex: 0 0 40px;
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: center;
	background-color: var(--backgroundColor);
	border-bottom: 1px solid var(--separatorColor);
	padding: 0;
}

.CorePDF .controls span {
	flex: 0 0 fit-content;
	text-align: left;
	padding: 0 10px;
}

.CorePDF .controls button {
	display: flex;
	height: 40px;
	width: 40px;
	line-height: 40px;
	text-align: center;
	border-radius: 4px;
	flex: 0 0 40px;
	border: none;
	cursor: pointer;
	background: none;
	align-items: center;
	justify-content: center;
}
.CorePDF .controls button i {
	line-height: 40px;
	text-align: center;
	vertical-align: middle;
	color: var(--primaryTextColor);
}

.CorePDF .controls button:hover {
	border: 1px solid black;
}

.CorePDF .controls > .separator {
	flex: 1;
}

.CorePDF .viewer {
	flex: 1;
	overflow: auto;
	position: relative;
	background-color: var(--containerBackgroundColor);
}

.CorePDF .viewer .page {
	margin-bottom: 3px;
	overflow: hidden;
}

.CorePDF .viewer .page:last-child {
	margin-bottom: 0;
}

.CorePDF .viewer .page > div {
	width: fit-content;
	margin: 0 auto;
}

.CorePDF .mask {
	pointer-events: none;
}

.CorePDF.beingEdited .mask {
	pointer-events: auto;
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0);
}

.CorePDF.beingEdited.selected .mask {
	pointer-events: none;
}
</style>
