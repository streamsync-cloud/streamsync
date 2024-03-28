<template>
	<div
		ref="rootEl"
		class="CoreAvatar"
		:class="[fields.size.value, fields.orientation.value]"
	>
		<div class="image" @click="handleClick">
			<i v-if="!fields.imageSrc.value" class="ri-user-line"></i>
		</div>
		<div class="info">
			<div v-if="fields.name.value" class="name" @click="handleClick">
				{{ fields.name.value }}
			</div>
			<div v-if="fields.caption.value" class="caption">
				{{ fields.caption.value }}
			</div>
			<div class="container" data-streamsync-container>
				<slot></slot>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
import { FieldCategory, FieldType } from "../../streamsyncTypes";
import {
	cssClasses,
	primaryTextColor,
	secondaryTextColor,
	separatorColor,
} from "../../renderer/sharedStyleFields";
import { getClick } from "../../renderer/syntheticEvents";

const clickHandlerStub = `
def handle_avatar_click():
	print("The avatar was clicked")`;

const description = "A component to display user avatars.";

export default {
	streamsync: {
		name: "Avatar",
		description,
		category: "Content",
		allowedChildrenTypes: ["*"],
		fields: {
			name: {
				name: "Name",
				type: FieldType.Text,
			},
			imageSrc: {
				name: "Image source",
				desc: "A valid URL. Alternatively, you can provide a state reference to a packed file.",
				type: FieldType.Text,
			},
			caption: {
				name: "Caption",
				desc: "Add an optional caption under the name, such as the person's job title.",
				type: FieldType.Text,
			},
			size: {
				name: "Size",
				type: FieldType.Text,
				options: {
					small: "Small",
					medium: "Medium",
					large: "Large",
				},
				default: "medium",
				category: FieldCategory.Style,
			},
			orientation: {
				name: "Orientation",
				type: FieldType.Text,
				options: {
					horizontal: "Horizontal",
					vertical: "Vertical",
				},
				default: "horizontal",
				category: FieldCategory.Style,
			},
			primaryTextColor,
			secondaryTextColor,
			separatorColor,
			cssClasses,
		},
		events: {
			"ss-click": {
				desc: "Triggered when the avatar is clicked.",
				stub: clickHandlerStub.trim(),
			},
		},
		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { Ref, computed, inject, ref } from "vue";
import injectionKeys from "../../injectionKeys";

const rootEl: Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);
const componentId = inject(injectionKeys.componentId);
const ss = inject(injectionKeys.core);

const isClickable = computed(() => {
	const component = ss.getComponentById(componentId);
	return typeof component.handlers?.["ss-click"] !== "undefined";
});

function handleClick(ev: MouseEvent) {
	const ssEv = getClick(ev);
	rootEl.value.dispatchEvent(ssEv);
}
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreAvatar {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	flex-direction: row;
}

.CoreAvatar.small {
	gap: 12px;
}

.CoreAvatar.medium {
	gap: 24px;
}

.CoreAvatar.large {
	gap: 24px;
}

.CoreAvatar.vertical {
	flex-direction: column;
}

.image {
	display: flex;
	overflow: hidden;
	align-items: center;
	justify-content: center;
	border-radius: 50%;
	background-color: var(--separatorColor);
	background-position: center;
	background-size: cover;
	background-image: v-bind(
		"fields.imageSrc.value ? `url(\"${fields.imageSrc.value}\")` : 'none'"
	);
	color: var(--primaryTextColor);
	cursor: v-bind("isClickable ? 'pointer' : 'auto'");
}

.image i {
	opacity: 0.3;
}

.info {
	display: flex;
	flex-direction: column;
	gap: 8px;
	color: var(--primaryTextColor);
}

.vertical .info {
	align-items: center;
}

.small .image {
	font-size: 18px;
	height: 36px;
	width: 36px;
}

.medium .image {
	font-size: 36px;
	height: 72px;
	width: 72px;
}

.large .image {
	font-size: 64px;
	height: 128px;
	width: 128px;
}

.name {
	font-weight: bold;
	cursor: v-bind("isClickable ? 'pointer' : 'auto'");
}

.small .name {
	font-size: 0.8rem;
}

.medium .name {
	font-size: 0.9rem;
}

.large .name {
	font-size: 1.2rem;
}

.info .caption {
	color: var(--secondaryTextColor);
}

.container {
	margin-top: 8px;
}

.container:empty {
	display: none;
}
</style>
