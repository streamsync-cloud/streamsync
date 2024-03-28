<docs lang="md">
Use your app's static folder to serve videos directly. For example, \`static/my_video.mp4\`.

Alternatively, you can pack bytes or files in state:

\`state["vid_b"] = ss.pack_bytes(vid_bytes, "video/mp4")\`

\`state["vid_f"] = ss.pack_file(vid_file, "video/mp4")\`

Afterwards, you can reference the video using the syntax \`@{vid_f}\`.
</docs>

<template>
	<div class="CoreVideoPlayer">
		<video
			:src="fields.src.value"
			:controls="fields.controls.value === 'yes'"
			:autoplay="fields.autoplay.value === 'yes'"
			:loop="fields.loop.value === 'yes'"
			:muted="fields.muted.value === 'yes'"
		></video>
		<div class="mask" />
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const description =
	"A video player component that can play various video formats.";

export default {
	streamsync: {
		name: "Video Player",
		description,
		category: "Content",
		fields: {
			src: {
				name: "Source",
				desc: "The URL of the video file. Alternatively, you can pass a file via state.",
				default: "",
				type: FieldType.Text,
			},
			controls: {
				name: "Controls",
				desc: "Display video player controls.",
				default: "yes",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			autoplay: {
				name: "Autoplay",
				desc: "Autoplay the video when the component is loaded.",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			loop: {
				name: "Loop",
				desc: "Loop the video when it reaches the end.",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			muted: {
				name: "Muted",
				desc: "Mute the video by default.",
				default: "no",
				type: FieldType.Text,
				options: {
					yes: "Yes",
					no: "No",
				},
			},
			cssClasses,
		},
	},
};
</script>

<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "../../injectionKeys";

const fields = inject(injectionKeys.evaluatedFields);
</script>

<style scoped>
.CoreVideoPlayer {
	position: relative;
	width: 100%;
}

video {
	width: 100%;
}

.mask {
	pointer-events: none;
}

.beingEdited .mask {
	pointer-events: auto;
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0);
}

.beingEdited.selected .mask {
	pointer-events: none;
}
</style>
