// Maps Writer Framework component types to renderable Vue components
// content
import CoreDataframe from "../core_components/content/CoreDataframe.vue";
import CoreHeading from "../core_components/content/CoreHeading.vue";
import CoreIcon from "../core_components/content/CoreIcon.vue";
import CoreImage from "../core_components/content/CoreImage.vue";
import CoreMessage from "../core_components/content/CoreMessage.vue";
import CoreMetric from "../core_components/content/CoreMetric.vue";
import CorePlotlyGraph from "../core_components/content/CorePlotlyGraph.vue";
import CoreText from "../core_components/content/CoreText.vue";
import CoreVegaLiteChart from "../core_components/content/CoreVegaLiteChart.vue";
import CoreVideoPlayer from "../core_components/content/CoreVideoPlayer.vue";
import CoreLink from "../core_components/content/CoreLink.vue";
import CoreChatbot from "../core_components/content/CoreChatbot.vue";
import CoreTags from "../core_components/content/CoreTags.vue";
import CoreAvatar from "../core_components/content/CoreAvatar.vue";
// input
import CoreCheckboxInput from "../core_components/input/CoreCheckboxInput.vue";
import CoreDateInput from "../core_components/input/CoreDateInput.vue";
import CoreDropdownInput from "../core_components/input/CoreDropdownInput.vue";
import CoreFileInput from "../core_components/input/CoreFileInput.vue";
import CoreMultiselectInput from "../core_components/input/CoreMultiselectInput.vue";
import CoreNumberInput from "../core_components/input/CoreNumberInput.vue";
import CoreRadioInput from "../core_components/input/CoreRadioInput.vue";
import CoreSelectInput from "../core_components/input/CoreSelectInput.vue";
import CoreSliderInput from "../core_components/input/CoreSliderInput.vue";
import CoreTextInput from "../core_components/input/CoreTextInput.vue";
import CoreTextareaInput from "../core_components/input/CoreTextareaInput.vue";
import CoreTimeInput from "../core_components/input/CoreTimeInput.vue";
import CoreRating from "../core_components/input/CoreRatingInput.vue";
import CoreSwitchInput from "../core_components/input/CoreSwitchInput.vue";
// layout
import CoreColumn from "../core_components/layout/CoreColumn.vue";
import CoreColumns from "../core_components/layout/CoreColumns.vue";
import CoreHeader from "../core_components/layout/CoreHeader.vue";
import CoreHorizontalStack from "../core_components/layout/CoreHorizontalStack.vue";
import CoreSection from "../core_components/layout/CoreSection.vue";
import CoreSeparator from "../core_components/layout/CoreSeparator.vue";
import CoreSidebar from "../core_components/layout/CoreSidebar.vue";
import CoreTab from "../core_components/layout/CoreTab.vue";
import CoreTabs from "../core_components/layout/CoreTabs.vue";
import CoreStep from "../core_components/layout/CoreStep.vue";
import CoreSteps from "../core_components/layout/CoreSteps.vue";
// other
import CoreButton from "../core_components/other/CoreButton.vue";
import CoreHtml from "../core_components/other/CoreHtml.vue";
import CorePagination from "../core_components/other/CorePagination.vue";
import CoreRepeater from "../core_components/other/CoreRepeater.vue";
import CoreTimer from "../core_components/other/CoreTimer.vue";
import CoreWebcamCapture from "../core_components/other/CoreWebcamCapture.vue";
import CoreReuse from "../core_components/other/CoreReuse.vue";
// embed
import CorePDF from "../core_components/embed/CorePDF.vue";
import CoreIFrame from "../core_components/embed/CoreIFrame.vue";
import CoreGoogleMaps from "../core_components/embed/CoreGoogleMaps.vue";
// root
import CorePage from "../core_components/root/CorePage.vue";
import CoreRoot from "../core_components/root/CoreRoot.vue";

import CoreMapbox from "../core_components/embed/CoreMapbox.vue";

import { WriterComponentDefinition } from "../writerTypes";
import { h } from "vue";

const templateMap = {
	root: CoreRoot,
	page: CorePage,
	sidebar: CoreSidebar,
	button: CoreButton,
	text: CoreText,
	section: CoreSection,
	header: CoreHeader,
	heading: CoreHeading,
	dataframe: CoreDataframe,
	html: CoreHtml,
	pagination: CorePagination,
	repeater: CoreRepeater,
	column: CoreColumn,
	columns: CoreColumns,
	tab: CoreTab,
	tabs: CoreTabs,
	link: CoreLink,
	horizontalstack: CoreHorizontalStack,
	separator: CoreSeparator,
	image: CoreImage,
	pdf: CorePDF,
	iframe: CoreIFrame,
	googlemaps: CoreGoogleMaps,
	mapbox: CoreMapbox,
	icon: CoreIcon,
	timer: CoreTimer,
	textinput: CoreTextInput,
	textareainput: CoreTextareaInput,
	numberinput: CoreNumberInput,
	sliderinput: CoreSliderInput,
	dateinput: CoreDateInput,
	timeinput: CoreTimeInput,
	radioinput: CoreRadioInput,
	checkboxinput: CoreCheckboxInput,
	dropdowninput: CoreDropdownInput,
	selectinput: CoreSelectInput,
	multiselectinput: CoreMultiselectInput,
	fileinput: CoreFileInput,
	webcamcapture: CoreWebcamCapture,
	vegalitechart: CoreVegaLiteChart,
	plotlygraph: CorePlotlyGraph,
	metric: CoreMetric,
	message: CoreMessage,
	videoplayer: CoreVideoPlayer,
	chatbot: CoreChatbot,
	step: CoreStep,
	steps: CoreSteps,
	ratinginput: CoreRating,
	tags: CoreTags,
	switchinput: CoreSwitchInput,
	reuse: CoreReuse,
	avatar: CoreAvatar,
};

if (WRITER_LIVE_CCT === "yes") {
	/*
	Assigns the components in custom_components to the template map,
	allowing for live updates when developing custom component templates. 
	*/

	const liveCCT: Record<string, any> = (await import("../custom_components"))
		.default;
	Object.entries(liveCCT).forEach(([componentType, template]) => {
		templateMap[`custom_${componentType}`] = template;
	});
}

function fallbackTemplate(type: string) {
	const message = `Component type "${type}" not supported. If it's a custom component, please ensure it's been loaded.`;
	return {
		writer: {
			name: "Fallback Component",
			allowedChildrenTypes: ["*"],
			description: message,
			category: "Fallback",
		},
		setup(props, { slots }) {
			return () => {
				return h(
					"div",
					{
						"data-writer-container": "",
						style: {
							color: "var(--primaryTextColor)",
						},
					},
					[message, slots.default({})],
				);
			};
		},
	};
}

export function getTemplate(type: string) {
	return templateMap[type] ?? fallbackTemplate(type);
}

export function getComponentDefinition(
	type: string,
): WriterComponentDefinition {
	return getTemplate(type)?.writer;
}

export function getSupportedComponentTypes() {
	return Object.keys(templateMap);
}

export function registerComponentTemplate(type: string, vueComponent: any) {
	templateMap[type] = vueComponent;
}

export default templateMap;
