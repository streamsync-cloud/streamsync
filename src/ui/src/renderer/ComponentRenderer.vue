<template>
	<main
		class="ComponentRenderer"
		tabindex="-1"
		:style="rootStyle"
		:class="{ loadingActive: isMessagePending }"
	>
		<RendererNotifications class="notifications"></RendererNotifications>
		<div class="loadingBar"></div>
		<div class="rootComponentArea">
			<ComponentProxy
				v-if="rootComponent"
				:component-id="rootComponent.id"
				:instance-path="rootInstancePath"
				:instance-data="rootInstanceData"
			></ComponentProxy>
			<slot></slot>
		</div>
	</main>
</template>

<script setup lang="ts">
import { inject, ref, Ref, computed, watch } from "vue";
import { Component, InstancePath } from "../streamsyncTypes";
import ComponentProxy from "./ComponentProxy.vue";
import RendererNotifications from "./RendererNotifications.vue";
import injectionKeys from "../injectionKeys";
import { useEvaluator } from "./useEvaluator";

const ss = inject(injectionKeys.core);
const templateEvaluator = useEvaluator(ss);
const rootComponent: Component = ss.getComponentById("root");

if (!rootComponent) {
	// eslint-disable-next-line no-console
	console.error("No root component found.");
}

const rootInstancePath: InstancePath = [
	{ componentId: "root", instanceNumber: 0 },
];
const rootInstanceData = [ref(null)];
const rootFields = templateEvaluator.getEvaluatedFields(rootInstancePath);
const rootStyle = computed(() => {
	return {
		"--accentColor": rootFields.accentColor?.value,
		"--emptinessColor": rootFields.emptinessColor?.value,
		"--containerBackgroundColor": rootFields.parentIdBackgroundColor?.value,
		"--primaryTextColor": rootFields.primaryTextColor?.value,
		"--secondaryTextColor": rootFields.secondaryTextColor?.value,
		"--separatorColor": rootFields.separatorColor?.value,
	};
});

const isMessagePending = computed(() => {
	const frontendMessageMap = ss.getFrontendMessageMap();
	return frontendMessageMap.size > 0;
});

watch(
	() => rootFields.appName?.value,
	(appName: string) => {
		updateTitle(appName);
	},
	{ immediate: true },
);

function updateTitle(appName: string) {
	const mode = ss.getMode();
	let title: string;
	if (appName && mode == "edit") {
		title = `${appName} | Streamsync Builder`;
	} else if (!appName && mode == "edit") {
		title = "Streamsync Builder";
	} else if (appName && mode == "run") {
		title = `${appName}`;
	} else if (!appName && mode == "run") {
		title = "Streamsync App";
	}
	document.title = title;
}
</script>

<style scoped>
@import "./sharedStyles.css";

.ComponentRenderer {
	--accentColor: #29cf00;
	--buttonColor: #ffffff;
	--emptinessColor: #e9eef1;
	--separatorColor: rgba(0, 0, 0, 0.07);
	--primaryTextColor: #202829;
	--buttonTextColor: #202829;
	--secondaryTextColor: #5d7275;
	--containerBackgroundColor: #ffffff;
	width: 100%;
	outline: none;
	--notificationsDisplacement: 0;
	font-family: Inter, sans-serif;
	font-size: 0.8rem;
	color: var(--primaryTextColor);
	background: var(--emptinessColor);
	display: flex;
	flex-direction: column;
	min-height: 100%;
	isolation: isolate;
	flex: 1 0 auto;
}
.notifications {
	right: var(--notificationsDisplacement);
}

.loadingBar {
	width: 100%;
	height: 4px;
	margin-bottom: -4px;
	position: sticky;
	top: 0;
	pointer-events: none;
	z-index: 4;
	transition-delay: 0.2s;
	transition-property: opacity;
	transition-duration: 200ms;
	opacity: 0;
}

.loadingActive .loadingBar {
	background-size: 200% 200%;
	opacity: 1;
	animation: loadingAnimation ease-in-out 1s infinite;
	animation-delay: 200ms;
	background-image: linear-gradient(
		270deg,
		var(--emptinessColor),
		var(--accentColor),
		var(--emptinessColor)
	);
}

@keyframes loadingAnimation {
	0% {
		background-position: 0% 0%;
	}
	50% {
		background-position: 100% 100%;
	}
	100% {
		background-position: 0% 0%;
	}
}
.rootComponentArea {
	display: flex;
	flex: 1 0 auto;
}
</style>
