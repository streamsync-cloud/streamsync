import { FieldCategory, FieldType } from "../streamsyncTypes";

export const accentColor = {
	name: "Accent",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const primaryTextColor = {
	name: "Primary text",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const secondaryTextColor = {
	name: "Secondary text",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const emptinessColor = {
	name: "Emptiness",
	desc: "Page background color",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const containerBackgroundColor = {
	name: "Container background",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const containerShadow = {
	name: "Container shadow",
	type: FieldType.Shadow,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const separatorColor = {
	name: "Separator",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const buttonColor = {
	name: "Button",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const buttonTextColor = {
	name: "Button text",
	type: FieldType.Color,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const buttonShadow = {
	name: "Button shadow",
	type: FieldType.Shadow,
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const selectedColor = {
	name: "Selected",
	type: FieldType.Color,
	default: "rgba(210, 234, 244, 0.8)",
	category: FieldCategory.Style,
	applyStyleVariable: true,
};

export const cssClasses = {
	name: "Custom CSS classes",
	type: FieldType.Text,
	category: FieldCategory.Style,
	desc: "CSS classes, separated by spaces. You can define classes in custom stylesheets.",
};

export const contentWidth = {
	name: "Content width",
	type: FieldType.Width,
	default: "100%",
	category: FieldCategory.Style,
	desc: "Configure content width using CSS units, e.g. 100px, 50%, 10vw, etc.",
};

export const contentHAlign = {
	name: "Content alignment (H)",
	type: FieldType.HAlign,
	default: "unset",
	category: FieldCategory.Style,
};

export const contentVAlign = {
	name: "Content alignment (V)",
	type: FieldType.VAlign,
	default: "unset",
	category: FieldCategory.Style,
};

export const contentPadding = {
	name: "Padding",
	type: FieldType.Padding,
	default: "0",
	category: FieldCategory.Style,
};
