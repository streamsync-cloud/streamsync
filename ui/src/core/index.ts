/* eslint-disable @typescript-eslint/ban-types */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { ref, Ref, computed, isRef, ComputedRef } from "vue";
import {
	Component,
	ComponentMap,
	InstancePath,
	MailItem,
	UserFunction,
	StreamsyncComponentDefinition,
} from "../streamsyncTypes";
import {
	getSupportedComponentTypes,
	getComponentDefinition,
} from "./templateMap";
import * as typeHierarchy from "./typeHierarchy";
import { auditAndFixComponents } from "./auditAndFix";
import { parseAccessor } from "./parsing";
import { loadExtensions } from "./loadExtensions";

const RECONNECT_DELAY_MS = 1000;
const KEEP_ALIVE_DELAY_MS = 60000;

export function generateCore() {
	let sessionId: string = null;
	const sessionTimestamp: Ref<number> = ref(null);
	const componentDefinitionOverrides: Ref<
		Partial<StreamsyncComponentDefinition>
	> = ref({});
	const mode: Ref<"run" | "edit"> = ref(null);
	const runCode: Ref<string> = ref(null);
	const components: Ref<ComponentMap> = ref({});
	const userFunctions: Ref<UserFunction[]> = ref([]);
	const userState: Ref<Record<string, any>> = ref({});
	let webSocket: WebSocket;
	const syncHealth: Ref<"idle" | "connected" | "offline"> = ref("idle");
	let frontendMessageCounter = 0;
	const frontendMessageMap: Ref<Map<number, { callback?: Function }>> = ref(
		new Map(),
	);
	let mailInbox: MailItem[] = [];
	const mailSubscriptions: { mailType: string; fn: Function }[] = [];
	const activePageId: Ref<Component["id"]> = ref(null);

	function getFrontendMessageMap() {
		return frontendMessageMap.value;
	}

	/**
	 * Whether Streamsync is running as builder or runner.
	 * The mode is enforced in the backend and used in the frontend for presentation purposes only.
	 *
	 * @returns
	 */
	function getMode() {
		return mode.value;
	}

	/**
	 * Initialise the core.
	 * @returns
	 */
	async function init() {
		await initSession();
		addMailSubscription("pageChange", (pageKey: string) => {
			setActivePageFromKey(pageKey);
		});
		sendKeepAliveMessage();
		if (mode.value != "edit") return;
	}

	/**
	 * Initialise a session by loading a starter pack from the backend.
	 *
	 * @returns
	 */
	async function initSession() {
		const response = await fetch("./api/init", {
			method: "post",
			cache: "no-store",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				proposedSessionId: sessionId,
			}),
		});
		const initData = await response.json();

		if (response.status > 400) {
			throw "Connection rejected.";
		}

		if (initData.extensionPaths) {
			await loadExtensions(initData.extensionPaths);
		}

		mode.value = initData.mode;
		components.value = initData.components;
		userState.value = initData.userState;
		collateMail(initData.mail);
		sessionId = initData.sessionId;
		sessionTimestamp.value = new Date().getTime();

		// Only returned for edit (Builder) mode

		userFunctions.value = initData.userFunctions;
		runCode.value = initData.runCode;

		await startSync();

		if (mode.value != "edit") return;
		const isFixApplied = auditAndFixComponents(initData.components);
		if (!isFixApplied) return;
		await sendComponentUpdate();
	}

	function getSessionTimestamp() {
		return sessionTimestamp.value;
	}

	function sendKeepAliveMessage() {
		setTimeout(() => {
			sendFrontendMessage("keepAlive", {}, sendKeepAliveMessage);
		}, KEEP_ALIVE_DELAY_MS);
	}

	function ingestMutations(mutations: Record<string, any>) {
		if (!mutations) return;
		Object.entries(mutations).forEach(([key, value]) => {
			/*
			Splits the key while respecting escaped dots.
			For example, "files.myfile\.sh" will be split into ["files", "myfile.sh"] 
			*/

			const mutationFlag = key.charAt(0);
			const accessor = parseAccessor(key.substring(1));
			const lastElementIndex = accessor.length - 1;
			let stateRef = userState.value;

			// Check if the accessor is meant for deletion.
			const isDeletion = mutationFlag === "-";

			for (let i = 0; i < lastElementIndex; i++) {
				const nextStateRef = stateRef?.[accessor[i]];
				if (typeof nextStateRef === "object" && nextStateRef !== null) {
					stateRef = nextStateRef;
				} else if (!isDeletion) {
					// Only create new path elements if it's not a deletion operation.
					stateRef[accessor[i]] = {};
					stateRef = stateRef[accessor[i]];
				}
			}

			if (isDeletion) {
				// If it's a deletion operation, delete the property.
				delete stateRef[accessor.at(-1)];
			} else {
				// Otherwise, set the value as usual.
				stateRef[accessor.at(-1)] = value;
			}
		});
	}

	function ingestComponents(newComponents: Record<string, any>) {
		if (!newComponents) return;
		components.value = newComponents;
	}

	function clearFrontendMap() {
		frontendMessageMap.value.forEach(({ callback }) => {
			callback?.({ ok: false });
		});
		frontendMessageMap.value.clear();
	}

	// Open and setup websocket

	async function startSync(): Promise<void> {
		if (webSocket) return; // Open WebSocket exists

		const url = new URL("./api/stream", window.location.href);
		url.protocol = url.protocol.replace("https", "wss");
		url.protocol = url.protocol.replace("http", "ws");
		webSocket = new WebSocket(url.href);

		webSocket.onopen = () => {
			clearFrontendMap();
			syncHealth.value = "connected";
			console.log("WebSocket connected. Initialising stream...");
			sendFrontendMessage("streamInit", { sessionId });
		};

		webSocket.onmessage = (wsEvent) => {
			const message = JSON.parse(wsEvent.data);

			if (
				message.messageType == "announcement" &&
				message.payload.announce == "codeUpdate"
			) {
				webSocket.close();
				initSession();
				return;
			} else if (
				message.messageType == "eventResponse" ||
				message.messageType == "stateEnquiryResponse"
			) {
				ingestMutations(message.payload?.mutations);
				collateMail(message.payload?.mail);
				ingestComponents(message.payload?.components);
			}

			const mapItem = frontendMessageMap.value.get(message.trackingId);
			mapItem?.callback?.({ ok: true, payload: message.payload });
			frontendMessageMap.value.delete(message.trackingId);
		};

		webSocket.onclose = async (ev: CloseEvent) => {
			webSocket = null;
			syncHealth.value = "offline";

			if (ev.code == 1008) {
				// 1008: Policy Violation
				// Connection established correctly but closed due to invalid session.
				// Do not attempt to reconnect, the session will remain invalid. Initialise a new session.

				console.error("Invalid session. Reinitialising...");

				// Take care of pending event resolutions and fail them.
				await initSession();
				return;
			}

			// Connection lost due to some other reason. Try to reconnect.

			console.error("WebSocket closed. Attempting to reconnect...");
			setTimeout(async () => {
				try {
					await startSync();
				} catch {
					console.error("Couldn't reconnect.");
				}
			}, RECONNECT_DELAY_MS);
		};

		return new Promise((resolve, reject) => {
			webSocket.addEventListener("open", () => resolve(), { once: true });
			webSocket.addEventListener("close", () => reject(), { once: true });
		});
	}

	/**
	 * Dispatches the given mail to the relevant mail subscriptions.
	 * Items that cannot be distributed remain in the inbox.
	 *
	 * @param mail
	 * @returns
	 */
	function collateMail(mail: MailItem[] = []) {
		mailInbox.push(...mail);
		mailInbox = mailInbox.filter((item) => {
			const relevantSubscriptions = mailSubscriptions.filter(
				(ms) => ms.mailType == item.type,
			);

			if (relevantSubscriptions.length == 0) {
				return item;
			}

			relevantSubscriptions.forEach((ms) => ms.fn(item.payload));
		});
	}

	function addMailSubscription(mailType: string, fn: Function) {
		mailSubscriptions.push({ mailType, fn });
		collateMail();
	}

	function getPayloadFromEvent(event: Event) {
		let eventPayload = null;

		if (event instanceof CustomEvent) {
			eventPayload = event.detail?.payload ?? null;
		} else {
			const simplifiedEvent = {};
			for (const i in event) {
				const value = event[i];
				if (typeof value === "function") continue;
				if (value instanceof Object) continue;
				simplifiedEvent[i] = value;
			}
			eventPayload = simplifiedEvent;
		}

		return eventPayload;
	}

	async function forwardEvent(
		event: Event,
		instancePath: InstancePath,
		includeEventPayload: boolean,
	) {
		const eventPayload = includeEventPayload
			? getPayloadFromEvent(event)
			: null;
		let callback: Function;

		if (event instanceof CustomEvent) {
			callback = event.detail?.callback;
		}

		const messagePayload = async () => ({
			type: event.type,
			instancePath,
			payload: await eventPayload,
		});

		sendFrontendMessage("event", messagePayload, callback, true);
	}

	async function sendCodeSaveRequest(newCode: string): Promise<void> {
		const messageData = {
			code: newCode,
		};

		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) {
					reject("Couldn't connect to the server.");
					return;
				}
				resolve();
			};

			sendFrontendMessage(
				"codeSaveRequest",
				messageData,
				messageCallback,
			);
		});
	}

	async function sendCodeUpdate(newCode: string): Promise<void> {
		const messageData = {
			code: newCode,
		};

		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) {
					reject("Couldn't connect to the server.");
					return;
				}
				resolve();
			};
			sendFrontendMessage("codeUpdate", messageData, messageCallback);
		});
	}

	async function sendStateEnquiry(callback: Function) {
		sendFrontendMessage("stateEnquiry", {}, callback, true);
	}

	function getRunCode() {
		return runCode.value;
	}

	function setupMessageFollowUp(trackingId: number) {
		const INITIAL_FOLLOWUP_MS = 100;
		const SUBSEQUENT_FOLLOWUPS_MS = 1000;

		const checkIfStateEnquiryRequired = () => {
			const isPending = frontendMessageMap.value.has(trackingId);
			if (!isPending) return;
			sendStateEnquiry(() =>
				setTimeout(
					checkIfStateEnquiryRequired,
					SUBSEQUENT_FOLLOWUPS_MS,
				),
			);
		};
		setTimeout(checkIfStateEnquiryRequired, INITIAL_FOLLOWUP_MS);
	}

	async function sendFrontendMessage(
		type: string,
		payload: object | (() => Promise<object>),
		callback?: Function,
		track = false,
	) {
		const trackingId = frontendMessageCounter++;
		try {
			if (callback || track) {
				frontendMessageMap.value.set(trackingId, {
					callback,
				});
			}
			if (track) {
				setupMessageFollowUp(trackingId);
			}

			let awaitedPayload: object;
			if (typeof payload == "function") {
				awaitedPayload = await payload();
			} else {
				awaitedPayload = payload;
			}

			const wsData = {
				type,
				trackingId,
				payload: awaitedPayload,
			};
			if (webSocket.readyState !== webSocket.OPEN) {
				throw "Connection lost.";
			}
			webSocket.send(JSON.stringify(wsData));
		} catch {
			callback?.({ ok: false });
		}
	}

	function deleteComponent(componentId: Component["id"]) {
		delete componentDefinitionOverrides.value[componentId];
		delete components.value[componentId];
	}

	function addComponent(component: Component) {
		components.value[component.id] = component;
	}

	/**
	 * Triggers a component update.
	 * @returns
	 */
	async function sendComponentUpdate(): Promise<void> {
		/*
 		Ensure that the backend receives only components 
		created by the frontend (Builder-managed components, BMC), 
		and not the components it generated (Code-managed components, CMC).
 		*/

		const builderManagedComponents = {};

		Object.entries(components.value).forEach(([componentId, component]) => {
			if (component.flag === "cmc") return;
			builderManagedComponents[componentId] = component;
		});

		const payload = {
			components: builderManagedComponents,
		};

		return new Promise((resolve, reject) => {
			const messageCallback = (r: {
				ok: boolean;
				payload?: Record<string, any>;
			}) => {
				if (!r.ok) {
					reject("Couldn't connect to the server.");
					return;
				}
				resolve();
			};
			sendFrontendMessage("componentUpdate", payload, messageCallback);
		});
	}

	function getUserFunctions() {
		return userFunctions.value;
	}

	function getComponentById(componentId: Component["id"]): Component {
		return components.value[componentId];
	}

	function isChildOf(parentId: Component["id"], childId: Component["id"]) {
		let child = components.value[childId];
		do {
			if (child.parentId == parentId) return true;
			child = components.value[child.parentId];
		} while (child);
		return false;
	}

	/**
	 * Gets registered Streamsync components.
	 *
	 * @param childrenOfId If specified, only include results that are children of a component with this id.
	 * @param sortedByPosition Whether to sort the components by position or return in random order.
	 * @returns An array of components.
	 */
	function getComponents(
		childrenOfId: Component["id"] = undefined,
		sortedByPosition: boolean = false,
	): Component[] {
		let ca = Object.values(components.value);

		if (typeof childrenOfId != "undefined") {
			ca = ca.filter((c) => c.parentId == childrenOfId);
		}
		if (sortedByPosition) {
			ca = ca.sort((a, b) => (a.position > b.position ? 1 : -1));
		}
		return ca;
	}

	function setActivePageFromKey(targetPageKey: string) {
		const pages = getComponents("root");
		const matches = pages.filter((pageComponent) => {
			const pageKey = pageComponent.content["key"];
			return pageKey == targetPageKey;
		});
		if (matches.length == 0) return;
		setActivePageId(matches[0].id);
	}

	function getPageKeys() {
		const pages = getComponents("root");
		const pageKeys = pages
			.map((page) => page.content["key"])
			.filter((pageKey) => !!pageKey);
		return pageKeys;
	}

	function setActivePageId(componentId: Component["id"]) {
		activePageId.value = componentId;
	}

	function getActivePageId(): Component["id"] {
		return activePageId.value;
	}

	function getContainableTypes(componentId: Component["id"]) {
		return typeHierarchy.getContainableTypes(components.value, componentId);
	}

	function getUserState() {
		return userState.value;
	}

	function getComponentDefinitionById(
		componentId: Component["id"] | Ref<Component["id"]>,
	): ComputedRef<StreamsyncComponentDefinition> {
		return computed(() => {
			const id: Component["id"] = isRef(componentId)
				? componentId.value
				: componentId;
			const component = components.value[id];
			if (!component) return null;
			return {
				...getComponentDefinition(component.type),
				...(componentDefinitionOverrides.value[id] || {}),
			};
		});
	}

	function setComponentDefinitionById(
		componentId: Component["id"],
		patch: Partial<StreamsyncComponentDefinition>,
	) {
		return (componentDefinitionOverrides.value[componentId] = patch);
	}

	function getInstancePath(componentId: Component["id"]): InstancePath {
		const path = [];
		let currentId = componentId;
		while (currentId) {
			const component = components.value[currentId];
			path.unshift({ componentId: component.id, instanceNumber: 0 });
			currentId = component.parentId;
		}
		return path;
	}
	function getComponentPageId(componentId: Component["id"]): Component["id"] {
		let currentId = componentId;
		while (currentId) {
			const component = components.value[currentId];
			if (component.type == "page") return component.id;
			currentId = component.parentId;
		}
		return null;
	}

	const core = {
		webSocket,
		syncHealth,
		getFrontendMessageMap,
		getMode,
		getUserFunctions,
		addMailSubscription,
		init,
		forwardEvent,
		getRunCode,
		sendCodeSaveRequest,
		sendCodeUpdate,
		sendComponentUpdate,
		addComponent,
		deleteComponent,
		getComponentById,
		getComponents,
		setActivePageId,
		getActivePageId,
		getPageKeys,
		setActivePageFromKey,
		getComponentDefinition,
		getSupportedComponentTypes,
		getContainableTypes,
		getSessionTimestamp,
		getUserState,
		isChildOf,
		getComponentDefinitionById,
		setComponentDefinitionById,
		getInstancePath,
		getComponentPageId,
	};

	return core;
}
