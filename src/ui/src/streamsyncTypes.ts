import { generateCore } from "./core";
import { generateBuilderManager } from "./builder/builderManager";

export type Core = ReturnType<typeof generateCore>;

type ComponentId = string;

/**
 * Basic building block of applications.
 * Multiple instances of a single component can exists. For example, via Repeater.
 */

export type Component = {
	id: ComponentId;
	parentId: string;
	type: string;
	position: number;
	content: Record<string, string>;
	isCodeManaged?: boolean;
	handlers?: Record<string, string>;
	visible?: boolean | string;
	binding?: {
		eventType: string;
		stateRef: string;
	};
};

/**
 * Identifies a unique instance of a Component.
 */

export type InstancePathItem = {
	componentId: Component["id"];
	instanceNumber: number;
};

/**
 * Details the full path, including all ancestors, of a unique instance of a Component.
 */

export type InstancePath = InstancePathItem[];

/**
 * Defines component structure and behaviour. Included in Component templates.
 */

export type StreamsyncComponentDefinition = {
	name: string; // Display name for the component
	description: string; // Short description
	docs?: string; // Collapsible mini-docs
	category?: string; // Category (Layout, Content, etc)
	allowedChildrenTypes?: (string | "*" | "inherit")[]; // Which component types are allowed inside (if any)
	allowedParentTypes?: string[]; // Which component types can contain this type of component
	fields?: Record<
		string, // Id for the field
		{
			name: string; // Display name
			init?: string; // Initial value
			desc?: string; // Description
			default?: string; // Value used if the field is empty, e.g. "(No text)"
			control?: FieldControl; // Which control (text, textarea, etc) to use if not the default for the type
			options?:
				| Record<string, string>
				| ((
						ss?: Core,
						componentId?: ComponentId,
				  ) => Record<string, string>); // List of values to be provided as autocomplete options
			type: FieldType; // Data type for the field
			category?: FieldCategory; // Category (Layout, Content, etc)
			applyStyleVariable?: boolean; // Use the value of this field as a CSS variable
		}
	>;
	events?: Record<
		string, // Event type
		{
			desc?: string; // Description
			stub?: string; // Stub method for the event
			bindable?: boolean; // Whether this event is used for value binding
		}
	>;
	previewField?: string; // Which field to use for previewing in the Component Tree
	positionless?: boolean; // Whether this type of component is positionless (like Sidebar)
};

export type BuilderManager = ReturnType<typeof generateBuilderManager>;

export const enum ClipboardOperation {
	Cut = "cut",
	Copy = "copy",
}

export const enum FieldType {
	Text = "Text",
	KeyValue = "Key-Value",
	Color = "Color",
	Shadow = "Shadow",
	Number = "Number",
	Object = "Object",
	IdKey = "Identifying Key",
	Width = "Width",
	HAlign = "Align (H)",
	VAlign = "Align (V)",
	Padding = "Padding",
}

export const enum FieldCategory {
	General = "General",
	Style = "Style",
}

/**
 * Used to specify the field control if it's different from the default for the FieldType.
 */
export const enum FieldControl {
	Text = "Text",
	Textarea = "Textarea",
}

export type ComponentMap = Record<Component["id"], Component>;

/**
 * Unit of data for non-state-mutation communications between frontend and backend.
 */
export type MailItem = { type: string; payload: Record<string, string> };

export type UserFunction = { name: string; args: string[] };
