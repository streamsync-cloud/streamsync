import type {
	JsonData,
	JsonValue,
	JsonViewerTogglePayload,
} from "./BaseJsonViewer.vue";

export function isJSONValue(data: JsonData): data is JsonValue {
	if (["string", "number", "boolean"].includes(typeof data)) return true;
	if (data === null) return true;
	return false;
}

export function isJSONArray(data: JsonData): data is JsonData[] {
	if (isJSONValue(data)) return false;
	return Array.isArray(data);
}

export function isJSONObject(
	data: JsonData,
): data is { [x: string]: JsonData } {
	return !isJSONArray(data) && typeof data === "object" && data !== null;
}

export function getJSONLength(data: JsonData): number {
	return isJSONValue(data) ? 1 : Object.keys(data).length;
}

export function jsonViewerToggleEmitDefinition(
	payload: JsonViewerTogglePayload,
) {
	return typeof payload.open === "boolean" && Array.isArray(payload.path);
}
