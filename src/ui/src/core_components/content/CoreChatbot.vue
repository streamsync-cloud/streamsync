<docs lang="md">
Connect it to an LLM by handling the \`ss-chatbot-message\` event, which is triggered every time the user sends a message. When the response is ready, return it.

You can add \`actions\` to your response, which are buttons that trigger the \`ss-chatbot-action-click\`.

See the stubs for more details.
</docs>
<template>
	<div ref="rootEl" class="CoreChatbot">
		<div ref="messageAreaEl" class="messageArea">
			<div ref="messagesEl" class="messages">
				<div
					v-for="(message, messageId) in messages"
					:key="messageId"
					class="message"
					:class="message.origin"
				>
					<div class="avatar">
						{{
							message.origin == "incoming"
								? fields.incomingInitials.value
								: fields.outgoingInitials.value
						}}
					</div>
					<div class="contents">
						<div v-if="message.isLoading" class="loadingContainer">
							<LoadingSymbol
								class="loadingSymbol"
							></LoadingSymbol>
						</div>
						<template v-else>
							<div class="text">
								<BaseMarkdown
									v-if="
										message.origin == 'incoming' &&
										fields.useMarkdown.value == 'yes'
									"
									:raw-text="message.contents.text"
								>
								</BaseMarkdown>
								<template v-else>
									{{ message.contents.text }}
								</template>
							</div>
							<div
								v-if="message.contents.actions"
								class="actions"
							>
								<button
									v-for="(action, actionIndex) in message
										.contents.actions"
									:key="actionIndex"
									class="action"
									@click="handleActionClick(action)"
								>
									<div
										v-if="action.subheading"
										class="subheading"
									>
										{{ action.subheading }}
									</div>
									<h3 class="name">{{ action.name }}</h3>
									<div v-if="action.desc" class="desc">
										{{ action.desc }}
									</div>
								</button>
							</div>
						</template>
					</div>
					<div
						v-if="message.date"
						class="time"
						:title="getFormattedDate(message.date, false)"
					>
						{{ getFormattedDate(message.date, true) }}
					</div>
				</div>
			</div>
		</div>
		<template v-if="files.length > 0">
			<div class="filesArea">
				<template v-if="isUploadingFiles">
					<LoadingSymbol class="loadingSymbol"></LoadingSymbol>

					Uploading...
				</template>
				<div v-if="!isUploadingFiles" class="list">
					<div
						v-for="(file, fileIndex) in files"
						:key="fileIndex"
						class="file"
					>
						<div>
							<div class="name" :title="file.name">
								{{ file.name }}
							</div>
							<div class="size">
								{{ prettyBytes(file.size) }}
							</div>
						</div>
						<button
							variant="subtle"
							@click="handleRemoveFile(fileIndex)"
						>
							<i class="ri-close-line"></i>
						</button>
					</div>
				</div>
			</div>
			<div class="filesButtons">
				<button
					v-if="!isUploadSizeExceeded && !isUploadingFiles"
					class="uploadButton"
					@click="handleUploadFiles"
				>
					<i class="ri-upload-line"></i>Upload
				</button>
				<div v-if="isUploadSizeExceeded" class="sizeExceededMessage">
					<i class="ri-file-warning-line"></i> Size limit of
					{{ prettyBytes(MAX_FILE_SIZE) }} exceeded.
				</div>
			</div>
		</template>
		<div class="inputArea">
			<textarea
				v-model="outgoingMessage"
				:placeholder="fields.placeholder.value"
				@keydown.prevent.enter="handleMessageSent"
			></textarea>
		</div>
		<div class="inputButtons">
			<button title="Send message" @click="handleMessageSent">
				<i class="ri-send-plane-line"></i>
			</button>
			<button
				v-if="fields.enableFileUpload.value != 'no'"
				title="Attach files"
				@click="handleAttachFiles"
			>
				<i class="ri-attachment-line"></i>
			</button>
		</div>
	</div>
</template>

<script lang="ts">
import LoadingSymbol from "../../renderer/LoadingSymbol.vue";
import BaseMarkdown from "../base/BaseMarkdown.vue";
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import {
	buttonColor,
	buttonTextColor,
	containerBackgroundColor,
	cssClasses,
	primaryTextColor,
	secondaryTextColor,
	separatorColor,
} from "../../renderer/sharedStyleFields";
import prettyBytes from "pretty-bytes";

const MAX_FILE_SIZE = 200 * 1024 * 1024;

const description = "A chatbot component to build human-to-AI interactions.";

const chatbotMessageStub = `
def handle_message_simple(payload):
    query = payload

    if query == "Hello":

		# You can simply return a string

        return "Hello, human."
    elif query == "Surprise me":

		# Or you can return a dict with actions, which are buttons
		# added to the conversation

        return {
            "text": "I can help you with that.",
            "actions": [{
            	"subheading": "Resource",
            	"name": "Surprise",
            	"desc": "Click to be surprised",
            	"data": "change_title" 
        	}]
        }
    else:
        return "I don't know"
`.trim();

const chatbotActionClickStub = `
def handle_action_simple(payload, state):
    
    # payload contains the "data" property of the action 
    
    if payload == "change_title":
        state["app_title"] = "Surprise!"
        state["app_background_color"] = "red"
    
    # A message can be added to the chat
    
    return "Hope you're surprised."
`.trim();

const fileChangeStub = `
def handle_file_upload(state, payload):

	# An array of dictionaries is provided in the payload
	# The dictionaries have the properties name, type and data
    # The data property is a file-like object

    uploaded_files = payload
    for i, uploaded_file in enumerate(uploaded_files):
		name = uploaded_file.get("name")
        file_data = uploaded_file.get("data")
        with open(f"{name}-{i}.jpeg", "wb") as file_handle:
            file_handle.write(file_data)`.trim();

export default {
	streamsync: {
		name: "Chatbot",
		description,
		category: "Content",
		fields: {
			incomingInitials: {
				name: "Incoming initials",
				default: "AI",
				type: FieldType.Text,
			},
			outgoingInitials: {
				name: "Outgoing initials",
				default: "YOU",
				type: FieldType.Text,
			},
			useMarkdown: {
				name: "Use Markdown",
				desc: "It'll only be applied to incoming messages. The output will be sanitised; unsafe elements will be removed.",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			enableFileUpload: {
				name: "Enable file upload",
				default: "no",
				type: FieldType.Text,
				options: {
					single: "Single file",
					multiple: "Multiple files",
					no: "No",
				},
			},
			placeholder: {
				name: "Placeholder",
				default: "Write something...",
				type: FieldType.Text,
			},
			incomingColor: {
				name: "Incoming",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
			},
			outgoingColor: {
				name: "Outgoing",
				default: "#F5F5F9",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
			},
			avatarBackgroundColor: {
				name: "Avatar",
				default: "#2C2D30",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
			},
			avatarTextColor: {
				name: "Avatar text",
				default: "#FFFFFF",
				type: FieldType.Color,
				category: FieldCategory.Style,
				applyStyleVariable: true,
			},
			containerBackgroundColor,
			primaryTextColor,
			secondaryTextColor,
			separatorColor,
			buttonColor,
			buttonTextColor,
			cssClasses,
		},
		events: {
			"ss-chatbot-message": {
				desc: "Triggered when the user sends a message.",
				stub: chatbotMessageStub,
			},
			"ss-chatbot-action-click": {
				desc: "Handle clicks on actions.",
				stub: chatbotActionClickStub,
			},
			"ss-file-change": {
				desc: "Triggered when files are uploaded",
				stub: fileChangeStub,
			},
		},
	},
};
</script>
<script setup lang="ts">
import {
	type Ref,
	onMounted,
	onBeforeUnmount,
	shallowRef,
	inject,
	ref,
	computed,
} from "vue";
import injectionKeys from "../../injectionKeys";

type Message = {
	origin: "incoming" | "outgoing";
	isLoading?: boolean;
	date?: Date;
	contents: {
		text: string;
		actions?: {
			subheading?: string;
			name: string;
			desc?: string;
			data?: string;
		}[];
	};
};

const rootEl: Ref<HTMLElement> = ref(null);
const messageAreaEl: Ref<HTMLElement> = ref(null);
const messagesEl: Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);
const messages: Ref<Record<string, Message>> = ref({});
const files: Ref<File[]> = shallowRef([]);
const isUploadingFiles = ref(false);
let messageCounter = 0;
let resizeObserver: ResizeObserver;

const outgoingMessage: Ref<string> = ref("");

const isUploadSizeExceeded = computed(() => {
	let filesSize = 0;
	Array.from(files.value).forEach((file) => {
		filesSize += file.size;
	});
	return filesSize >= MAX_FILE_SIZE;
});

function getFormattedDate(date: Date, isTimeOnly: boolean) {
	if (!date) return;

	if (!isTimeOnly) {
		return date.toLocaleString();
	}

	const options: Intl.DateTimeFormatOptions = {
		hour: "numeric",
		minute: "numeric",
		hour12: true,
	};
	return date.toLocaleTimeString(undefined, options);
}

function addMessage(message: Message) {
	messageCounter += 1;
	const messageKey = `msg${messageCounter}`;
	messages.value[messageKey] = message;
	return messageKey;
}

function replaceMessage(messageKey: string, message: Message) {
	messages.value[messageKey] = message;
}

function handleMessageSent() {
	addMessage({
		origin: "outgoing",
		contents: {
			text: outgoingMessage.value,
		},
		date: new Date(),
	});
	const outgoingMessageKey = addMessage({
		origin: "incoming",
		contents: {
			text: "Loading...",
		},
		isLoading: true,
	});
	const event = new CustomEvent("ss-chatbot-message", {
		detail: {
			payload: outgoingMessage.value,
			callback: ({ payload }) => {
				const callbackResult = payload?.result?.result;
				if (!callbackResult) return;
				replaceMessage(outgoingMessageKey, {
					origin: "incoming",
					contents: getNormalisedCallbackResult(callbackResult),
					date: new Date(),
				});
			},
		},
	});
	rootEl.value.dispatchEvent(event);
	outgoingMessage.value = "";
}

/**
 * Allows strings to be sent from the backend as a substitute of Message["contents"].
 *
 * @param callbackResult
 */
function getNormalisedCallbackResult(
	callbackResult: string | Message["contents"],
): Message["contents"] {
	if (typeof callbackResult == "string") {
		return {
			text: callbackResult,
		};
	}
	return callbackResult;
}

function handleActionClick(action: Message["contents"]["actions"][number]) {
	const { data } = action;
	const event = new CustomEvent("ss-chatbot-action-click", {
		detail: {
			payload: data,
			callback: ({ payload }) => {
				const callbackResult = payload?.result?.result;
				if (!callbackResult) return;
				addMessage({
					origin: "incoming",
					contents: getNormalisedCallbackResult(callbackResult),
					date: new Date(),
				});
			},
		},
	});
	rootEl.value.dispatchEvent(event);
}

function handleAttachFiles() {
	const el: HTMLInputElement = document.createElement("input");
	el.type = "file";
	if (fields.enableFileUpload.value == "multiple") {
		el.multiple = true;
	}
	el.addEventListener("change", () => {
		// A new list is created to allow shallowRef to detect the change

		let newList: File[];
		if (fields.enableFileUpload.value == "multiple") {
			newList = [...files.value];
		} else {
			newList = [];
		}
		Array.from(el.files).forEach((file) => {
			newList.push(file);
		});
		files.value = newList;
	});
	el.dispatchEvent(new MouseEvent("click"));
}

function handleRemoveFile(index: number) {
	const newList = files.value.toSpliced(index, 1);
	files.value = newList;
}

function scrollToBottom() {
	messageAreaEl.value.scrollTo({
		top: messageAreaEl.value.scrollHeight,
		left: 0,
	});
}

const encodeFile = async (file: File) => {
	var reader = new FileReader();
	reader.readAsDataURL(file);

	return new Promise((resolve, reject) => {
		reader.onload = () => resolve(reader.result);
		reader.onerror = () => reject(reader.error);
	});
};

async function handleUploadFiles() {
	if (files.value.length == 0) return;
	if (isUploadingFiles.value) return;

	isUploadingFiles.value = true;

	const getPayload = async () => {
		let accumSize = 0;
		const encodedFiles = Promise.all(
			Array.from(files.value).map(async (f) => {
				accumSize += f.size;
				const fileItem = {
					name: f.name,
					type: f.type,
					data: await encodeFile(f),
				};
				return fileItem;
			}),
		);
		if (accumSize > MAX_FILE_SIZE) {
			alert("Size limit exceeded.");
			return;
		}
		return encodedFiles;
	};

	const payload = await getPayload();
	if (!payload) {
		isUploadingFiles.value = false;
		return;
	}

	const event = new CustomEvent("ss-file-change", {
		detail: {
			payload,
			callback: ({ payload }) => {
				isUploadingFiles.value = false;
				files.value = [];
				const callbackResult = payload?.result?.result;
				if (!callbackResult) return;
				addMessage({
					origin: "incoming",
					contents: getNormalisedCallbackResult(callbackResult),
					date: new Date(),
				});
			},
		},
	});

	rootEl.value.dispatchEvent(event);
}
onMounted(() => {
	/**
	 * A ResizeObserver allows the component to scroll to the bottom when a
	 * new message is added or grows in size. For example, after markdown rendering is finished.
	 *
	 * CSS overflow-anchor wasn't used due to problematic support in Safari.
	 */

	resizeObserver = new ResizeObserver(() => {
		scrollToBottom();
	});

	/**
	 * ResizeObserver only watches the client height, not the scroll height.
	 * So it's the element inside that needs to be watched to detect changes.
	 */

	resizeObserver.observe(messagesEl.value);
});

onBeforeUnmount(() => {
	resizeObserver.unobserve(messagesEl.value);
});
</script>
<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreChatbot {
	display: grid;
	grid-template-columns: 1fr fit-content(20%);
	grid-template-rows: 1fr fit-content(20%) 20%;
	height: 80vh;
	border-radius: 8px;
	overflow: hidden;
	background: var(--containerBackgroundColor);
	border: 1px solid var(--separatorColor);
}

.messageArea {
	overflow-y: auto;
	overflow-x: hidden;
	border-bottom: 1px solid var(--separatorColor);
	grid-column: 1 / 3;
	grid-row: 1;
}

.messages {
	padding: 16px;
	display: flex;
	gap: 16px;
	flex-direction: column;
}

.message {
	display: flex;
	gap: 8px;
}

.message .avatar {
	border-radius: 50%;
	background: var(--avatarBackgroundColor);
	color: var(--avatarTextColor);
	height: 36px;
	width: 36px;
	flex: 0 0 36px;
	display: flex;
	font-weight: bold;
	align-items: center;
	justify-content: center;
	overflow: hidden;
	text-transform: uppercase;
}

.message .contents {
	border-radius: 8px;
	width: fit-content;
	flex: 0 1 auto;
	color: var(--primaryTextColor);
	white-space: pre-wrap;
}

.message .time {
	color: var(--secondaryTextColor);
	font-size: 0.7rem;
	align-self: end;
	text-wrap: nowrap;
}

.message.incoming .contents {
	background: v-bind(
		"fields.incomingColor.value ? fields.incomingColor.value : 'linear-gradient(264.27deg, rgb(245, 235, 255) 0.71%, rgb(255, 241, 237) 100%)'"
	);
}

.message.outgoing .contents {
	background: var(--outgoingColor);
}

.contents .loadingContainer {
	padding: 16px;
}

.contents .text {
	line-height: 2;
	padding: 12px 16px 12px 16px;
}

.contents .actions {
	padding: 16px;
	background: rgba(0, 0, 0, 0.02);
	display: flex;
	gap: 12px;
	flex-wrap: wrap;
}

.contents .actions .action {
	padding: 12px;
	border-radius: 4px;
	background: var(--containerBackgroundColor);
	overflow: hidden;
	line-height: normal;
	display: flex;
	gap: 4px;
	flex-direction: column;
	box-shadow: 0 2px 2px 0px rgba(0, 0, 0, 0.1);
	cursor: pointer;
	border: 0;
}

.action .subheading {
	color: var(--secondaryTextColor);
	font-size: 0.7rem;
}

.action .desc {
	font-size: 0.7rem;
}

.filesArea {
	grid-column: 1;
	grid-row: 2;
	border-bottom: 1px solid var(--separatorColor);
	overflow-y: auto;
}

.filesArea .list {
	padding: 16px;
	flex: 1 1 auto;
	display: flex;
	flex-wrap: wrap;
	align-items: flex-start;
	gap: 16px;
}

.file {
	background: var(--separatorColor);
	border-radius: 8px;
	display: flex;
	gap: 16px;
	align-items: center;
	padding: 8px;
	font-size: 0.7rem;
}

.file .name {
	min-width: 5ch;
	max-width: 20ch;
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
}

.file .size {
	margin-top: 4px;
	color: var(--secondaryTextColor);
}

.file button {
	border-radius: 8px;
	padding: 0;
	width: 24px;
	height: 24px;
	background: unset;
}

.filesButtons {
	grid-column: 2;
	grid-row: 2;
	padding: 16px;
	border-bottom: 1px solid var(--separatorColor);
	display: flex;
	flex-direction: column;
	justify-content: center;
}

.filesButtons .uploadButton {
	display: flex;
	gap: 8px;
	align-items: center;
}

.inputArea {
	grid-column: 1;
	grid-row: 3;
	text-align: right;
	display: flex;
	align-items: top;
}

.inputArea textarea {
	border: none;
	width: 100%;
	height: 100%;
	padding: 16px;
	resize: none;
	background: transparent;
	color: var(--primaryTextColor);
	font-size: 0.8rem;
}

.inputButtons {
	grid-column: 2;
	grid-row: 3;
	display: flex;
	padding: 16px;
	flex-direction: column;
	gap: 8px;
	align-items: flex-end;
}

.inputButtons button {
	height: fit-content;
	flex: 0 0 auto;
	display: flex;
	gap: 8px;
	align-items: center;
}
</style>
