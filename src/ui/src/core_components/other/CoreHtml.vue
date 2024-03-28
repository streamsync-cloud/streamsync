<docs lang="md">
You can configure the element type, styles, and attributes to fit your design requirements. You can link them to state for advanced use cases, such as custom animations.

All valid HTML tags are supported, including tags such as \`iframe\`, allowing you to embed external sites.

Take into account the potential risks of adding custom HTML to your app, including XSS. Be specially careful when injecting user-generated data.
</docs>
<script lang="ts">
import { h, inject } from "vue";
import { FieldControl, FieldType } from "../../streamsyncTypes";
import injectionKeys from "../../injectionKeys";
import { cssClasses } from "../../renderer/sharedStyleFields";

const defaultStyle = {
	padding: "16px",
	"min-height": "64px",
	"min-width": "64px",
	"border-radius": "8px",
	background:
		"linear-gradient(90deg, rgba(41,207,0,1) 0%, rgba(145,231,78,1) 100%)",
};

const description =
	"A generic component that creates customisable HTML elements, which can serve as containers for other components.";

export default {
	streamsync: {
		name: "HTML Element",
		description,
		category: "Other",
		allowedChildrenTypes: ["*"],
		fields: {
			element: {
				name: "Element",
				default: "div",
				type: FieldType.Text,
				desc: "Set the type of HTML element to create, e.g., 'div', 'section', 'span', etc.",
			},
			styles: {
				name: "Styles",
				default: null,
				init: JSON.stringify(defaultStyle, null, 2),
				type: FieldType.Object,
				desc: "Define the CSS styles to apply to the HTML element using a JSON object or a state reference to a dictionary.",
			},
			attrs: {
				name: "Attributes",
				default: null,
				type: FieldType.Object,
				desc: "Set additional HTML attributes for the element using a JSON object or a dictionary via a state reference.",
			},
			htmlInside: {
				name: "HTML inside",
				default: null,
				type: FieldType.Text,
				control: FieldControl.Textarea,
				desc: "Define custom HTML to be used inside the element. It will be wrapped in a div and rendered after children components.",
			},
			cssClasses,
		},
	},
	setup(props, { slots }) {
		const fields = inject(injectionKeys.evaluatedFields);
		return () => {
			let insideHtmlNode = undefined;
			if (fields.htmlInside.value) {
				insideHtmlNode = h("div", {
					innerHTML: fields.htmlInside.value,
				});
			}
			return h(
				fields.element.value,
				{
					...fields.attrs.value,
					class: "CoreHTML",
					"data-streamsync-container": "",
					style: fields.styles.value,
				},
				[slots.default({}), insideHtmlNode],
			);
		};
	},
};
</script>
