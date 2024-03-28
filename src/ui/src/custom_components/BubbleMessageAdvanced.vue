<docs lang="md">
This documentation will show in the collapsible mini-docs feature embedded in Builder.
You _can_ use **markdown**.
</docs>

<template>
	<div
		ref="rootEl"
		class="BubbleMessage"
		:class="{ rightOriented: fields.orientation.value == 'right' }"
	>
		<div class="triangle"></div>
		<div class="message">
			<!-- Shows the current value of the field "text" -->
			<div class="text">
				{{ fields.text.value }}
			</div>
			<div class="actions">
				<div class="action" @click="emitPinEvent">
					<i class="ri-pushpin-line"></i>
				</div>
				<div class="action" @click="emitFlagEvent">
					<i class="ri-flag-line"></i>
				</div>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
/*
Define the Streamsync-specific information for the template.
Consult the type StreamsyncComponentDefinition for an overview of all fields.
*/

const flagMessageHandlerStub = `
def handle_flag(state, payload):
	state["flagged_message_id"] = payload`;

const pinMessageHandlerStub = `
def handle_pin(state, payload):
	state["pinned_message_id"] = payload`;

const streamsync: StreamsyncComponentDefinition = {
	name: "Bubble Message (Advanced)",
	description: "Shows a message in the shape of a speech bubble.",
	category: "Content",

	// Fields will be editable via Streamsync Builder

	fields: {
		messageId: {
			name: "Message id",
			desc: "Unique id to identify the message when generating events.",
			init: "a1",
			type: FieldType.Text,
		},
		text: {
			name: "Text",
			desc: "The message to be displayed.",
			default: "(Empty message)",
			type: FieldType.Text,
			control: FieldControl.Textarea, // By default, the Text type uses a "Text" control
		},
		orientation: {
			name: "Orientation",
			category: FieldCategory.Style,
			type: FieldType.Text,
			options: {
				// Used for autocomplete
				left: "Pointing left",
				right: "Pointing right",
			},
		},
		bubbleColor: {
			name: "Bubble",
			default: "#CFEFF3",
			category: FieldCategory.Style,
			type: FieldType.Color,
			applyStyleVariable: true, // Will be accessible via var(--bubbleColor)
		},

		// The following are standard style fields that are imported

		primaryTextColor,
		separatorColor,
		containerBackgroundColor,
		cssClasses,
	},

	events: {
		"pin-message": {
			desc: "Emitted when the pin button is clicked.",
			stub: pinMessageHandlerStub,
		},
		"flag-message": {
			desc: "Emitted when the flag button is clicked.",
			stub: flagMessageHandlerStub,
		},
	},

	// Preview field is used in the Component Tree

	previewField: "text",
};

export default {
	streamsync,
};
</script>
<script setup lang="ts">
import {
	FieldCategory,
	FieldControl,
	FieldType,
	StreamsyncComponentDefinition,
} from "../streamsyncTypes";
import injectionKeys from "../injectionKeys";
import { inject, computed, ref, Ref } from "vue";

/* Standard style fields can be imported from "sharedStyleFields" 
to avoid repetition. */

import {
	separatorColor,
	cssClasses,
	primaryTextColor,
	containerBackgroundColor,
} from "../renderer/sharedStyleFields";

const rootEl: Ref<HTMLElement> = ref(null); // Root element is used to fire events

/*
The values for the fields defined earlier in the custom option
will be available using the evaluatedFields injection symbol.
*/

const fields = inject(injectionKeys.evaluatedFields);
const messageId = computed(() => fields.messageId.value);

/*
Streamsync uses DOM events to manage events.
Event types that don't exist in the browser are generated using
CustomEvent (https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent).
*/

/**
 * Emits a CustomEvent of type "flag-message" from the root element.
 * If an event handler has been set on Builder for the "flag-message"
 * event, it'll be forwarded to the backend.
 */
function emitFlagEvent() {
	/*
    When a custom event is caught, the "payload"
    property of the detail is used as payload. 
    */

	const payload = messageId.value;
	const event = new CustomEvent("flag-message", {
		detail: {
			payload,
		},
	});
	rootEl.value.dispatchEvent(event);
}

/**
 * Analog to emitFlagEvent, for "pin-message".
 */
function emitPinEvent() {
	const payload = messageId.value;
	const event = new CustomEvent("pin-message", {
		detail: {
			payload,
		},
	});
	rootEl.value.dispatchEvent(event);
}
</script>

<style scoped>
.BubbleMessage {
	width: fit-content;
	max-width: 100%;
	display: flex;
	position: relative;
	background: var(--containerBackgroundColor);
}

.triangle {
	flex: 0 0 auto;
	border-right: none;
	border-bottom: none;
	border-left: 12px solid var(--containerBackgroundColor);
	border-top: 12px solid var(--bubbleColor);
}

.rightOriented .triangle {
	border-left: none;
	border-bottom: none;
	border-right: 12px solid var(--containerBackgroundColor);
	border-top: 12px solid var(--bubbleColor);
	order: 2;
}

.message {
	flex: 1 0 auto;
	color: var(--primaryTextColor);
	background: var(--bubbleColor);
	border-radius: 0 12px 12px 12px;
	min-width: 160px;
}

.rightOriented .message {
	border-radius: 12px 0 12px 12px;
}

.actions {
	display: flex;
	gap: 8px;
	align-items: center;
	justify-content: right;
	padding: 8px;
}

.action {
	border-radius: 4px;
	padding: 4px;
}

.action:hover {
	background: var(--separatorColor);
}

.message .text {
	border-bottom: 1px solid var(--separatorColor);
	padding: 16px;
}
</style>
