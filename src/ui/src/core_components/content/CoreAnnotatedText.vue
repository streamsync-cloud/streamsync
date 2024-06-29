<template>
	<div class="AnnotatedText">
		<span v-for="(content, i) in fields.text.value" :key="content + i">
			<template v-if="typeof content === 'string'">{{
				content
			}}</template>
			<span
				v-if="Array.isArray(content)"
				class="annotation"
				:style="{ background: content[2] || generateColor(content[1]) }"
			>
				{{ content[0] }}
				<span v-if="content[1]" class="annotation-subject">{{
					getShortName(content[1])
				}}</span>
			</span>
		</span>
		<template v-if="fields.copyButtons.value === 'yes'">
			<div class="controls">
				<button
					class="control-button"
					@click="copyJSON(fields.text.value)"
				>
					Copy JSON
				</button>
				<button
					class="control-button"
					@click="copyText(fields.text.value)"
				>
					Copy raw
				</button>
			</div>
		</template>
	</div>
</template>

<script lang="ts">
import { cssClasses, primaryTextColor } from "../renderer/sharedStyleFields";
export default {
	writer: {
		name: "Annotated text",
		description: "Shows text with annotations",
		category: "Content",

		fields: {
			text: {
				name: "KeyValue",
				type: FieldType.Object,
				desc: "Value array with text/annotations. Must be a JSON string or a state reference to an array.",
				default: `["This ",["is", "Verb"]," some ",["annotated", "Adjective"],    ["text", "Noun"]," for those of ",["you", "Pronoun"]," who ",["like", "Verb"]," this sort of ",["thing", "Noun"],". ","And here's a ",["word", "", "#faf"]," with a fancy background but no label."]`,
			},
			referenceColor: {
				name: "Reference",
				desc: "The colour to be used as reference for chroma and luminance, and as the starting point for hue rotation.",
				type: FieldType.Color,
				default: "#5551FF",
				category: FieldCategory.Style,
			},
			seed: {
				name: "Seed value",
				desc: "Choose a different value to reshuffle colours.",
				type: FieldType.Number,
				default: "1",
				category: FieldCategory.Style,
			},
			rotateHue: {
				name: "Rotate hue",
				desc: "If active, rotates the hue depending on the content of the string. If turned off, the reference colour is always used.",
				type: FieldType.Text,
				options: {
					yes: "yes",
					no: "no",
				},
				default: "no",
				category: FieldCategory.Style,
			},
			copyButtons: {
				name: "Copy buttons",
				desc: "If active, adds a control bar with both copy text and JSON buttons.",
				type: FieldType.Text,
				options: {
					yes: "yes",
					no: "no",
				},
				default: "no",
				category: FieldCategory.Style,
			},
			primaryTextColor,
			cssClasses,
		},
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { FieldCategory, FieldType } from "../writerTypes";
import injectionKeys from "../injectionKeys";
import { inject } from "vue";
import chroma, { Color } from "chroma-js";

const fields = inject(injectionKeys.evaluatedFields);

const COLOR_STEPS = [
	{ h: -78, s: -34, l: 16 },
	{ h: -61, s: -37, l: 16 },
	{ h: -2, s: 0, l: 24 },
	{ h: -12, s: 0, l: 29 },
	{ h: 28, s: -20, l: 24 },
	{ h: -61, s: -95, l: 25 },
	{ h: -173, s: 0, l: 16 },
	{ h: -228, s: 0, l: 22 },
	{ h: 69, s: 0, l: 25 },
	{ h: 70, s: 0, l: 29 },
];

let currentSteps = [...COLOR_STEPS];
let subjectColorCache = {};
let lastSeed = fields.seed.value;

function generateColorCss(
	baseColor: Color,
	colorData: { h: number; s: number; l: number },
) {
	let genColor = baseColor
		.set(
			"hsl.h",
			`${Math.sign(colorData.h) == -1 ? "-" : "+"}${Math.abs(colorData.h)}`,
		)
		.set(
			"hsl.s",
			`${Math.sign(colorData.s) == -1 ? "-" : "+"}${Math.abs(colorData.s / 100.0)}`,
		)
		.set(
			"hsl.l",
			`${Math.sign(colorData.l) == -1 ? "-" : "+"}${Math.abs(colorData.l / 100.0)}`,
		);

	return genColor.css();
}

function calculateColorStep(s: string, stepsLength = COLOR_STEPS.length) {
	let hash = (fields.seed.value * 52673) & 0xffffffff;
	for (let i = 0; i < s.length; i++) {
		hash = ((i + 1) * s.charCodeAt(i)) ^ (hash & 0xffffffff);
	}
	const step = Math.abs(hash) % stepsLength;

	return step;
}

function generateColor(s: string) {
	if (fields.rotateHue.value == "no") {
		return fields.referenceColor.value;
	}

	const baseColor = chroma(fields.referenceColor.value);

	if (lastSeed !== fields.seed.value) {
		currentSteps = [...COLOR_STEPS];
		subjectColorCache = {};
		lastSeed = fields.seed.value;
	}

	if (subjectColorCache[s]) {
		return generateColorCss(baseColor, subjectColorCache[s]);
	}

	// If we run out of colors, reset the list
	if (currentSteps.length === 0) {
		currentSteps = [...COLOR_STEPS];
	}

	const colorStep = calculateColorStep(s, currentSteps.length);
	const colorData = currentSteps[colorStep];

	subjectColorCache[s] = colorData;
	currentSteps.splice(colorStep, 1);

	return generateColorCss(baseColor, colorData);
}

function copyText(arr: string[]) {
	const text = arr.reduce((acc, val) => {
		if (typeof val === "string") {
			return acc + val;
		}

		return acc + val[0];
	}, "");

	copyToClipboard({ text });
}

function copyJSON(arr: string[]) {
	try {
		copyToClipboard({ text: JSON.stringify(arr) });
	} catch (e) {
		copyToClipboard({ text: arr.join("") });
	}
}

function setClipboardData<T = unknown>(
	source: T & { clipboardData: DataTransfer | null | undefined },
	{ text, html }: { text?: string; html?: string },
): void {
	if (text) {
		source.clipboardData?.setData("text/plain", text);
		source.clipboardData?.setData("Text", text); // IE mimetype
	}

	if (html) {
		source.clipboardData?.setData("text/html", html);
	}
}

function copyToClipboard({
	text = "",
	html = "",
}: {
	text?: string;
	html?: string;
}): boolean {
	if (
		(window as any)?.clipboardData &&
		(window as any)?.clipboardData.setData
	) {
		// Internet Explorer-specific code path to prevent textarea being shown while dialog is visible.
		setClipboardData<any>(window, { text, html });

		return true;
	} else if (
		document.queryCommandSupported &&
		document.queryCommandSupported("copy")
	) {
		const copyListener = (event: ClipboardEvent) => {
			event.preventDefault();
			setClipboardData<ClipboardEvent>(event, { text, html });
		};

		document.addEventListener("copy", copyListener, false);

		const textarea = document.createElement("textarea");
		textarea.textContent = text || html;
		textarea.style.position = "fixed";
		document.body.appendChild(textarea);
		textarea.select();

		try {
			return document.execCommand("copy"); // Security exception may be thrown by some browsers.
		} catch (ex) {
			return false;
		} finally {
			document.body.removeChild(textarea);
			document.removeEventListener("copy", copyListener, false);
		}
	}

	return false;
}

const defaultShortNameDictionary = {
	verb: "Verb",
	adjective: "Adj",
	noun: "Noun",
	pronoun: "Pronoun",
};

function getShortName(name: string) {
	if (!name) {
		return "";
	}

	const lowerCaseName = name.toLowerCase();
	if (defaultShortNameDictionary[lowerCaseName]) {
		return `${defaultShortNameDictionary[lowerCaseName]}`;
	}

	return name[0].toUpperCase() + name.slice(1);
}
</script>

<style scoped>
.AnnotatedText {
	color: var(--primaryTextColor);
	line-height: 1.8;
}

.annotation {
	flex-direction: row;
	align-items: center;
	background: rgba(255, 164, 33, 0.4);
	border-radius: 0.5rem;
	padding: 0.08rem 0.5rem;
	overflow: hidden;
	line-height: 1;
	vertical-align: middle;
}

.annotation-subject {
	display: inline-flex;
	font-size: 0.6rem;
	margin-left: 1rem;
	opacity: 0.5;
	position: relative;
	vertical-align: middle;

	&::after {
		content: "";
		border-left: 1px solid;
		opacity: 0.1;
		position: absolute;
		top: 0px;
		left: -0.55rem;
		height: 10px;
	}
}

.controls {
	margin: 10px 0;
	display: flex;
	flex-direction: row;
	justify-content: flex-end;
}

.control-button {
	background-color: var(--buttonColor);
	border: none;
	border-radius: 0.5rem;
	color: white;
	cursor: pointer;
	font-size: 0.7rem;
	margin-right: 10px;
	padding: 0.25rem 0.5rem;

	&:hover {
		opacity: 0.9;
	}
}
</style>
