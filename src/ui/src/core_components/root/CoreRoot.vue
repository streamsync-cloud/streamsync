<template>
	<div ref="rootEl" class="CoreRoot" data-streamsync-container>
		<template v-for="(vnode, index) in getChildrenVNodes()" :key="index">
			<component
				:is="vnode"
				v-if="vnode.key === `${activePageId}:0`"
			></component>
		</template>
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import * as sharedStyleFields from "../../renderer/sharedStyleFields";
import { nextTick } from "vue";
import { useEvaluator } from "../../renderer/useEvaluator";

const ssHashChangeStub = `
def handle_hashchange(state, payload):
	# The payload is a dictionary with the page key and all the route variables in the URL hash.
	# For example, if the current URL is
	# http://localhost:3000/#main/animal=duck&colour=yellow
	# you will get the following dictionary
	# {
	#	"page_key": "main",
	#	"route_vars": {
	#		"animal": "duck",
	#		"colour": "yellow"
	#	}
	# }

	page_key = payload.get("page_key")
	route_vars = payload.get("route_vars")

	if not route_vars:
		return

	if route_vars.get("animal") == "duck":
		state["message"] = "You've navigated to the Duck zone."
	else:
		state["message"] = "You're not in the Duck zone.`.trim();

const description =
	"The root component of the application, which serves as the starting point of the component hierarchy.";

export default {
	streamsync: {
		name: "Root",
		category: "Root",
		description,
		allowedChildrenTypes: ["page"],
		fields: {
			appName: {
				name: "App name",
				type: FieldType.Text,
				desc: "The app name will be shown in the browser's title bar.",
			},
			...sharedStyleFields,
		},
		events: {
			"ss-hashchange": {
				desc: "Capture changes to the URL hash, including page key and route vars.",
				stub: ssHashChangeStub,
			},
		},
	},
};
</script>
<script setup lang="ts">
import { computed, inject, ref, Ref, watch, onBeforeMount } from "vue";
import injectionKeys from "../../injectionKeys";

const importedModulesSpecifiers: Record<string, string> = {};
const ss = inject(injectionKeys.core);
const ssbm = inject(injectionKeys.builderManager);
const getChildrenVNodes = inject(injectionKeys.getChildrenVNodes);
const rootEl: Ref<HTMLElement> = ref(null);
const { isComponentVisible } = useEvaluator(ss);

const getFirstPageId = () => {
	const pageComponents = ss.getComponents("root", {
		includeBMC: true,
		includeCMC: true,
		sortedByPosition: true,
	});
	if (pageComponents.length == 0) return null;
	const visiblePages = pageComponents.filter((c) => isComponentVisible(c.id));
	if (visiblePages.length == 0) return null;
	return visiblePages[0].id;
};

const hashRegex = /^((?<pageKey>[^/]*))?(\/(?<routeVars>.*))?$/;
const routeVarRegex = /^(?<key>[^=]+)=(?<value>.*)$/;
const activePageId = computed(() => ss.getActivePageId() ?? getFirstPageId());

watch(activePageId, (newPageId) => {
	const page = ss.getComponentById(newPageId);
	const pageKey = page.content?.["key"];
	if (ssbm && ssbm.getSelectedId() !== newPageId) {
		ssbm.setSelection(null);
	}
	nextTick().then(() => {
		window.scrollTo(0, 0);
		const rendererEl = document.querySelector(".ComponentRenderer");
		rendererEl.parentElement.scrollTo(0, 0);
	});
	changePageInHash(pageKey);
});

type ParsedHash = {
	pageKey?: string;
	routeVars: Record<string, string>;
};

function getParsedHash(): ParsedHash {
	const docHash = document.location.hash.substring(1);
	const hashMatchGroups = docHash.match(hashRegex)?.groups;
	let pageKey: string;
	let routeVars: Record<string, string> = {};

	if (!hashMatchGroups) return { pageKey, routeVars };

	pageKey = hashMatchGroups?.pageKey
		? decodeURIComponent(hashMatchGroups.pageKey)
		: undefined;

	const routeVarsSegments = hashMatchGroups.routeVars?.split("&") ?? [];
	routeVarsSegments.forEach((routeVarSegment) => {
		const matchGroups = routeVarSegment.match(routeVarRegex)?.groups;
		if (!matchGroups) return;
		const { key, value } = matchGroups;
		const decodedKey = decodeURIComponent(key);
		const decodedValue = decodeURIComponent(value);
		routeVars[decodedKey] = decodedValue;
	});

	return { pageKey, routeVars };
}

function setHash(parsedHash: ParsedHash) {
	const { pageKey, routeVars } = parsedHash;

	let hash = "";
	if (pageKey) {
		hash += `${encodeURIComponent(pageKey)}`;
	}
	if (Object.keys(routeVars).length > 0) {
		hash += "/";
		hash += Object.entries(routeVars)
			.map(([key, value]) => {
				// Vars set to null are excluded from the hash

				if (value === null) return null;
				return `${encodeURIComponent(key)}=${encodeURIComponent(
					value,
				)}`;
			})
			.filter((segment) => segment)
			.join("&");
	}
	document.location.hash = hash;
}

function changePageInHash(targetPageKey: string) {
	const parsedHash = getParsedHash();
	parsedHash.pageKey = targetPageKey;
	setHash(parsedHash);
}

function changeRouteVarsInHash(targetRouteVars: Record<string, string>) {
	const parsedHash = getParsedHash();
	const routeVars = parsedHash?.routeVars ?? {};
	parsedHash.routeVars = { ...routeVars, ...targetRouteVars };
	setHash(parsedHash);
}

function handleHashChange() {
	const parsedHash = getParsedHash();
	const event = new CustomEvent("ss-hashchange", {
		detail: {
			payload: parsedHash,
		},
	});
	rootEl.value?.dispatchEvent(event);
	if (!parsedHash.pageKey) return;
	ss.setActivePageFromKey(parsedHash.pageKey);
}

async function importStylesheet(stylesheetKey: string, path: string) {
	const existingEl = document.querySelector(
		`[data-streamsync-stylesheet-key="${stylesheetKey}"]`,
	);
	existingEl?.remove();
	const el = document.createElement("link");
	el.dataset.streamsyncStylesheetKey = stylesheetKey;
	el.setAttribute("href", path);
	el.setAttribute("rel", "stylesheet");
	document.head.appendChild(el);
}

async function importScript(scriptKey: string, path: string) {
	const existingEl = document.querySelector(
		`[data-streamsync-script-key="${scriptKey}"]`,
	);
	existingEl?.remove();
	const el = document.createElement("script");
	el.dataset.streamsyncScriptKey = scriptKey;
	el.src = path;
	el.setAttribute("rel", "modulepreload");
	document.head.appendChild(el);
}

async function importModule(moduleKey: string, specifier: string) {
	importedModulesSpecifiers[moduleKey] = specifier;
	await import(/* @vite-ignore */ specifier);
}

async function handleFunctionCall(
	moduleKey: string,
	functionName: string,
	args: any[],
) {
	const specifier = importedModulesSpecifiers[moduleKey];
	const m = await import(/* @vite-ignore */ specifier);

	if (!m) {
		// eslint-disable-next-line no-console
		console.warn(
			`The module with key "${moduleKey}" cannot be found. Please check that it has been imported.`,
		);
		return;
	}
	m[functionName](...args);
}

type FileDownloadMailItemPayload = {
	data: string;
	fileName: string;
};

function addMailSubscriptions() {
	ss.addMailSubscription(
		"fileDownload",
		(mailItem: FileDownloadMailItemPayload) => {
			const el = document.createElement("a");
			el.href = mailItem.data;
			el.download = mailItem.fileName;
			el.click();
		},
	);
	ss.addMailSubscription("openUrl", (url: string) => {
		const el = document.createElement("a");
		el.href = url;
		el.target = "_blank";
		el.rel = "noopener noreferrer";
		el.click();
	});
	ss.addMailSubscription("pageChange", (pageKey: string) => {
		changePageInHash(pageKey);
	});
	ss.addMailSubscription(
		"routeVarsChange",
		(routeVars: Record<string, string>) => {
			changeRouteVarsInHash(routeVars);
		},
	);
	ss.addMailSubscription(
		"importStylesheet",
		({ stylesheetKey, path }: { stylesheetKey: string; path: string }) => {
			importStylesheet(stylesheetKey, path);
		},
	);
	ss.addMailSubscription(
		"importScript",
		({ scriptKey, path }: { scriptKey: string; path: string }) => {
			importScript(scriptKey, path);
		},
	);
	ss.addMailSubscription(
		"importModule",
		({
			moduleKey,
			specifier,
		}: {
			moduleKey: string;
			specifier: string;
		}) => {
			importModule(moduleKey, specifier);
		},
	);
	ss.addMailSubscription(
		"functionCall",
		({
			moduleKey,
			functionName,
			args,
		}: {
			moduleKey: string;
			functionName: string;
			args: any[];
		}) => {
			handleFunctionCall(moduleKey, functionName, args);
		},
	);
}

onBeforeMount(() => {
	addMailSubscriptions();
	window.addEventListener("hashchange", () => {
		handleHashChange();
	});
	handleHashChange();
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreRoot {
	background: var(--emptinessColor);
	min-height: 100%;
	display: flex;
	width: 100%;
}

.CoreRoot.selected {
	background-color: var(--emptinessColor);
}
</style>
