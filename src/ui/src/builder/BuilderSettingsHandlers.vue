<template>
	<div v-if="ssbm.isSelectionActive()" class="BuilderSettingsHandlers">
		<div class="sectionTitle">
			<i class="ri-flashlight-line ri-xl"></i>
			<h3>Events</h3>
		</div>
		<div class="list">
			<div
				v-for="(eventInfo, eventType) in recognisedEvents"
				:key="eventType"
				class="fieldWrapper"
			>
				<div class="columns">
					<div class="fieldWrapperMain">
						<span class="name">{{ eventType }}</span>
						<select
							class="content"
							:value="component.handlers?.[eventType]"
							@input="handleHandlerChange($event, eventType)"
						>
							<option
								key="No handler"
								value=""
								:selected="!component.handlers?.[eventType]"
							>
								(No handler)
							</option>
							<option
								v-for="userFunction in userFunctions"
								:key="userFunction.name"
								:value="userFunction.name"
							>
								{{ userFunction.name }}
							</option>
							<option
								v-for="pageKey in pageKeys"
								:key="`$goToPage_${pageKey}`"
								:value="`$goToPage_${pageKey}`"
							>
								Go to page "{{ pageKey }}"
							</option>
							<template v-if="isHandlerInvalid(eventType)">
								<option
									:value="component.handlers?.[eventType]"
								>
									{{ component.handlers?.[eventType] }} (Not
									Found)
								</option>
							</template>
						</select>
					</div>
					<div class="fieldActions">
						<button
							v-if="getStubCode(eventType)"
							variant="subtle"
							title="Show event handler stub"
							@click="showStub(eventType)"
						>
							<i class="ri-question-line ri-lg"></i>
						</button>
					</div>
				</div>
				<div v-if="eventInfo?.desc" class="desc">
					{{ eventInfo.desc }}
				</div>
			</div>
		</div>
		<BuilderModal
			v-if="stubModal"
			:close-action="stubCloseAction"
			icon="question"
			:modal-title="stubModal?.modalTitle"
		>
			<div class="stubMessage">
				You can use the following stub code as a starting point for your
				event handler.
			</div>
			<div class="codeContainer">
				<code v-dompurify-html="stubModal.highlightedCodeHtml"> </code>
			</div>
			<button @click="copyToClipboard(stubModal.code)">
				<i class="ri-file-copy-line ri-lg"></i>
				Copy code to clipboard
			</button>
		</BuilderModal>
		<div class="customHandler">
			<button
				title="Add a custom event handler"
				@click="showCustomHandlerModal"
			>
				<i class="ri-add-line ri-lg"></i>Add custom handler
			</button>
			<BuilderModal
				v-if="customHandlerModal"
				:close-action="customHandlerModalCloseAction"
				icon="flashlight"
				modal-title="Add Custom Event Handler"
			>
				<div class="customHandlerModalForm">
					<div class="fieldWrapper">
						<div class="fieldWrapperMain">
							<span class="name">Event type</span>
							<input
								v-model="customHandlerModal.eventType"
								class="content"
								type="text"
								list="commonEventTypes"
							/>
							<datalist id="commonEventTypes">
								<option
									v-for="commonEventType in commonEventTypes"
									:key="commonEventType"
									:value="commonEventType"
								>
									{{ commonEventType }}
								</option>
							</datalist>
						</div>
						<span class="desc">Can be any event type.</span>
					</div>
					<div class="fieldWrapper">
						<div class="fieldWrapperMain">
							<span class="name">Handler function</span>
						</div>
						<select
							v-model="customHandlerModal.handlerFunctionName"
							class="content"
						>
							<option
								v-for="userFunction in userFunctions"
								:key="userFunction.name"
								:value="userFunction.name"
							>
								{{ userFunction.name }}
							</option>
							<option
								v-for="pageKey in pageKeys"
								:key="`$goToPage_${pageKey}`"
								:value="`$goToPage_${pageKey}`"
							>
								Go to page "{{ pageKey }}"
							</option>
						</select>
						<span class="desc"
							>The function that will handle the event.</span
						>
					</div>
				</div>

				<button @click="addCustomEventHandler()">
					<i class="ri-add-line ri-lg"></i>
					Add
				</button>
			</BuilderModal>
		</div>
	</div>
</template>

<script setup lang="ts">
import * as monaco from "monaco-editor";

import { computed, ComputedRef, inject, Ref, ref } from "vue";
import { useComponentActions } from "./useComponentActions";
import injectionKeys from "../injectionKeys";
import BuilderModal, { ModalAction } from "./BuilderModal.vue";
import { StreamsyncComponentDefinition } from "../streamsyncTypes";

const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);

const { setHandlerValue } = useComponentActions(ss, ssbm);
const component = computed(() => ss.getComponentById(ssbm.getSelectedId()));

const recognisedEvents: ComputedRef<StreamsyncComponentDefinition["events"]> =
	computed(() => {
		const { type } = component.value;
		const { events: supportedEvents } = ss.getComponentDefinition(type);

		const recEvents = { ...supportedEvents };

		Object.keys({ ...component.value.handlers }).forEach((eventType) => {
			if (recEvents[eventType]) return;
			recEvents[eventType] = { desc: "Custom event" };
		});

		return recEvents;
	});

const userFunctions = computed(() => ss.getUserFunctions());
const pageKeys = computed(() => ss.getPageKeys());

const isHandlerInvalid = (eventType: string) => {
	const handlerFunctionName = component.value.handlers?.[eventType];
	if (!handlerFunctionName) return false;

	// $ is reserved for frontend internal use, such as page change

	if (handlerFunctionName.startsWith("$")) {
		return false;
	}
	if (userFunctions.value.some((uf) => uf.name == handlerFunctionName))
		return false;
	return true;
};

const handleHandlerChange = (ev: Event, eventType: string) => {
	const handlerFunctionName = (ev.target as HTMLInputElement).value;
	setHandlerValue(component.value.id, eventType, handlerFunctionName);
};

type StubModal = {
	code: string;
	highlightedCodeHtml: string;
	modalTitle: string;
};

type CustomHandlerModal = {
	eventType: string;
	handlerFunctionName: string;
};

const stubModal: Ref<StubModal> = ref(null);
const customHandlerModal: Ref<CustomHandlerModal> = ref(null);

function getCustomEventStubCode() {
	return `
# When dealing with a DOM event, Streamsync generates a payload by serialising its
# primitive properties (non-Object, non-function properties).

# If the event is instead an instance of CustomEvent,
# it looks for a "payload" property inside the CustomEvent's "detail" property. 

def handle_keydown(state, payload):
	print(payload) # Shows all the properties captured

	key_activated = payload.get("key")
	if key_activated == "ArrowLeft":
		state["position"] += -10
	elif key_activated == "ArrowRight":
		state["position"] += 10

	`;
}

function getStubCode(eventType: string) {
	const { type } = component.value;
	const { events } = ss.getComponentDefinition(type);
	const event = events?.[eventType];

	if (!event) return getCustomEventStubCode();

	return event?.stub;
}

async function showStub(eventType: string) {
	const code = getStubCode(eventType);
	const highlightedCodeHtml = await monaco.editor.colorize(
		code.trim(),
		"python",
		{},
	);
	stubModal.value = {
		modalTitle: `"${eventType}" event`,
		code,
		highlightedCodeHtml,
	};
}

const commonEventTypes = [
	"click",
	"mousedown",
	"mouseup",
	"mouseenter",
	"mouseleave",
	"mousemove",
	"keydown",
	"keyup",
	"keypress",
	"input",
	"change",
	"submit",
	"focus",
	"blur",
	"resize",
	"scroll",
	"load",
];

function addCustomEventHandler() {
	const { eventType, handlerFunctionName } = customHandlerModal.value;
	setHandlerValue(component.value.id, eventType, handlerFunctionName);
	customHandlerModal.value = null;
}

const stubCloseAction: ModalAction = {
	desc: "Close",
	fn: () => {
		stubModal.value = null;
	},
};

function showCustomHandlerModal() {
	customHandlerModal.value = {
		eventType: null,
		handlerFunctionName: null,
	};
}

const customHandlerModalCloseAction: ModalAction = {
	desc: "Close",
	fn: () => {
		customHandlerModal.value = null;
	},
};

const copyToClipboard = (text: string) => {
	navigator.clipboard.writeText(text);
};
</script>

<style scoped>
@import "./sharedStyles.css";

.BuilderSettingsHandlers {
	padding: 24px;
}
.list {
	border-radius: 4px;
	overflow: hidden;
}

.fieldWrapper .columns {
	display: flex;
	gap: 12px;
	align-items: center;
	max-width: 100%;
}

.fieldWrapper .content {
	padding: 16px 8px 12px 8px;
	width: 100%;
}

.fieldActions > button {
	border-radius: 16px;
}

.customHandler {
	margin-top: 24px;
}

.addHandler .fields {
	display: flex;
	gap: 16px;
	margin-bottom: 16px;
}

.stubMessage {
	font-size: 0.8rem;
}

.codeContainer {
	white-space: pre-wrap;
	background: var(--builderSubtleHighlightColorSolid);
	padding: 16px;
	border-radius: 4px;
	font-family: Consolas, monospace;
	font-size: 0.85rem;
	margin-top: 12px;
	margin-bottom: 12px;
	overflow: hidden;
	text-overflow: ellipsis;
}

.codeContainer code {
	white-space: pre-wrap;
}

.customHandlerModalForm {
	display: flex;
	align-items: center;
	gap: 16px;
	margin-bottom: 16px;
}

.customHandlerModalForm .fieldWrapper {
	flex: 1 1 auto;
	margin-top: 0;
}
</style>
