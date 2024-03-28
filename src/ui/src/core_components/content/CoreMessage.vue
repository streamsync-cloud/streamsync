<docs lang="md">
    When working with operations that can succeed or fail, _Message_ can be useful. You can reserve a state element to be used for the outcome of the operation; empty messages aren't shown, so you can initialise it empty.
    Then, assign a message when the operation is completed.

    \`\`\`
    state["msg"] = ""

    if is_ok:
    	state["msg"] = "+It worked!"
    else:
    	state["msg"] = "-It failed"
    \`\`\`
</docs>

<template>
	<div
		v-if="messageWithoutPrefix || isBeingEdited"
		class="CoreMessage"
		:style="rootStyle"
		:class="severity"
	>
		<div class="messageBackground"></div>
		<div v-if="messageWithoutPrefix" class="message">
			<LoadingSymbol v-if="severity == 'loading'" class="loadingSymbol">
			</LoadingSymbol>
			<span>{{ messageWithoutPrefix }}</span>
		</div>
		<div v-else class="empty">
			<h2>Blank Message</h2>
		</div>
	</div>
</template>

<script lang="ts">
import LoadingSymbol from "../../renderer/LoadingSymbol.vue";
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import { cssClasses, primaryTextColor } from "../../renderer/sharedStyleFields";

const description =
	"A component that displays a message in various styles, including success, error, warning, and informational.";

export default {
	streamsync: {
		name: "Message",
		description,
		category: "Content",
		fields: {
			message: {
				name: "Message",
				type: FieldType.Text,
				desc: "Prefix with '+' for a success message, with '-' for error, '!' for warning, '%' for loading. No prefix for info. Leave empty to hide.",
			},
			successColor: {
				name: "Success",
				default: "#00B800",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			errorColor: {
				name: "Error",
				default: "#FB0000",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			warningColor: {
				name: "Warning",
				default: "#FB9600",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			infoColor: {
				name: "Info",
				default: "#00ADB8",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			loadingColor: {
				name: "Loading",
				default: "#00ADB8",
				type: FieldType.Color,
				category: FieldCategory.Style,
			},
			primaryTextColor,
			cssClasses,
		},
		previewField: "name",
	},
};
</script>
<script setup lang="ts">
import { computed, inject } from "vue";
import injectionKeys from "../../injectionKeys";

const fields = inject(injectionKeys.evaluatedFields);
const isBeingEdited = inject(injectionKeys.isBeingEdited);

const severity = computed(() => {
	const message: string = fields.message.value;
	if (!message) return "neutral";
	const firstChar = message.charAt(0);
	if (firstChar == "+") {
		return "success";
	} else if (firstChar == "-") {
		return "error";
	} else if (firstChar == "!") {
		return "warning";
	} else if (firstChar == "%") {
		return "loading";
	}
	return "info";
});

const messageWithoutPrefix = computed(() => {
	const message: string = fields.message.value;
	if (!message) return;
	const firstChar = message.charAt(0);
	if (
		firstChar == "+" ||
		firstChar == "-" ||
		firstChar == "!" ||
		firstChar == "%"
	) {
		return message.substring(1).trim();
	}
	return message;
});

const rootStyle = computed(() => {
	const severityColors = {
		error: fields.errorColor.value,
		success: fields.successColor.value,
		warning: fields.warningColor.value,
		info: fields.infoColor.value,
		loading: fields.loadingColor.value,
	};
	return {
		"--messageActiveSeverityColor": severityColors[severity.value],
	};
});
</script>
<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreMessage {
	color: var(--primaryTextColor);
	--messageActiveSeverityColor: var(--separatorColor);
	position: relative;
	border-color: var(--messageActiveSeverityColor);
	color: var(--messageActiveSeverityColor);
	background: white;
}

.messageBackground {
	position: absolute;
	width: 100%;
	height: 100%;
	opacity: 0.2;
	background-color: var(--messageActiveSeverityColor);
	transition: 0.2s background-color ease-in-out;
}

.message {
	border-left: 4px solid var(--messageActiveSeverityColor);
	padding: 16px;
	display: flex;
	align-items: center;
	gap: 16px;
}

.message span {
	filter: brightness(0.7);
}

.loadingSymbol {
	margin: -8px 0 -8px 0;
}

.empty {
	padding: 16px;
	background-color: var(--separatorColor);
}

.empty > h2 {
	text-align: center;
	color: var(--primaryTextColor);
	opacity: 0.8;
}
</style>
