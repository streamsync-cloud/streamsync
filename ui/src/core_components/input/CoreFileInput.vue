<template>
	<div class="CoreFileInput" ref="rootEl">
		<div
			class="inputContainer"
			v-if="!processingFiles"
			@dragover.prevent="handleDragOver"
			@drop.prevent="handleDrop"
			@dragleave="isFileHover = false"
			:class="{ fileHover: isFileHover }"
		>
			<label @click="fileEl.click">{{
				isFileHover ? "Click or Drop File" : "Click or Drop File"
			}}</label>
			<input
				type="file"
				ref="fileEl"
				v-on:change="fileChange($event as InputEvent)"
				:multiple="allowMultipleFilesFlag"
			/>
		</div>
		<div class="status" v-if="message || processingFiles">
			<LoadingSymbol
				class="loadingSymbol"
				v-if="processingFiles"
			></LoadingSymbol>
			<span v-if="processingFiles"
				>Processing {{ processingFiles.join(", ") }}...</span
			>
			<span v-if="message">{{ message }}</span>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const MAX_FILE_SIZE = 200 * 1024 * 1024;

const description = "A user input component that allows users to upload files.";

const onChangeHandlerStub = `
def onchange_handler(state, payload):

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
		name: "File Input",
		description,
		category: "Input",
		fields: {
			label: {
				name: "Label",
				init: "Input Label",
				type: FieldType.Text,
			},
			allowMultipleFiles: {
				name: "Allow multiple files",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			cssClasses,
		},
		events: {
			"ss-file-change": {
				desc: "Capture changes to this control.",
				stub: onChangeHandlerStub,
				bindable: true,
			},
		},
	},
	components: { LoadingSymbol },
};
</script>

<script setup lang="ts">
import LoadingSymbol from "../../renderer/LoadingSymbol.vue";
import { computed, inject, Ref, ref, watch } from "vue";
import injectionKeys from "../../injectionKeys";
import { useFormValueBroker } from "../../renderer/useFormValueBroker";

const fields = inject(injectionKeys.evaluatedFields);
const rootEl: Ref<HTMLInputElement> = ref(null);
const fileEl: Ref<HTMLInputElement> = ref(null);
const message: Ref<string> = ref(null);
const ss = inject(injectionKeys.core);
const instancePath = inject(injectionKeys.instancePath);
const processingFiles: Ref<string[]> = ref(null);
const isFileHover: Ref<boolean> = ref(false);
const { formValue, handleInput } = useFormValueBroker(ss, instancePath, rootEl);

const allowMultipleFilesFlag = computed(() => {
	return fields.allowMultipleFiles.value == "yes" ? true : undefined;
});

// Event handlers for drag-and-drop
const handleDragOver = (event: DragEvent) => {
	event.preventDefault();
	isFileHover.value = true;
};

const handleDrop = (event: DragEvent) => {
	event.preventDefault();
	isFileHover.value = false;

	const files = event.dataTransfer.files;
	handlefiles(files);
};

const encodeFile = async (file: File) => {
	var reader = new FileReader();
	reader.readAsDataURL(file);

	return new Promise((resolve, reject) => {
		reader.onload = () => resolve(reader.result);
		reader.onerror = () => reject(reader.error);
	});
};

const fileChange = async (ev: InputEvent) => {
	const el = ev.target as HTMLInputElement;
	handlefiles(el.files);
};

const handlefiles = async (Files: FileList) => {
	if (!Files || Files.length == 0) return;
	window.alert("handlefiles");

	const getValue = async () => {
		let accumSize = 0;
		message.value = null;
		const encodedFiles = Promise.all(
			Array.from(Files).map(async (f) => {
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
			message.value = `Files are too big. Total size limit is ${Math.floor(
				MAX_FILE_SIZE / Math.pow(1024, 2),
			)}mb.`;
			return [];
		}
		return encodedFiles;
	};

	processingFiles.value = Array.from(Files).map((file) => file.name);
	formValue.value = getValue();

	const customCallback = () => {
		processingFiles.value = null;
	};

	handleInput(getValue(), "ss-file-change", customCallback);
};

watch(formValue, (newValue: string) => {
	if (typeof newValue === "undefined" && fileEl.value) {
		fileEl.value.value = "";
	}
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreFileInput {
	width: 100%;
	aspect-ratio: 16 / 9;
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;

	gap: 16px;
	padding: 16px;
	border: 1px solid var(--separatorColor);
	border-radius: 8px;
	box-shadow: var(--containerShadow);
	background-color: var(--containerBackgroundColor);
}

.inputContainer {
	width: 100%;
	height: 100%;
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
}

label {
	display: block;
	margin-bottom: 8px;
	border-radius: 0.1rem;
	padding: 1rem;
	border: 1px solid var(--separatorColor);
	cursor: pointer;
}

label:hover {
	background-color: var(--separatorColor);
}

input {
	max-width: 70ch;
	width: 100%;
	margin: 0;
	display: none;
}

.fileHover {
	background-color: lightblue;
	/* Change to your desired hover color */
}

.status {
	display: flex;
	align-items: center;
	gap: 16px;
	min-height: 36px;
}

.status .loadingSymbol {
	flex: 0 0 24px;
}

.status span {
	text-overflow: ellipsis;
	white-space: nowrap;
	overflow: hidden;
}
</style>
