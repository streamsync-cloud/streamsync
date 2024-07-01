import type { InstancePath } from "../writerTypes";

export function flattenInstancePath(path: InstancePath) {
	return path.map((ie) => `${ie.componentId}:${ie.instanceNumber}`).join(",");
}

export function parseInstancePathString(raw?: string): InstancePath {
	if (!raw) return [];
	return raw.split(",").map((record) => {
		const [componentId, instanceNumber] = record.split(":");
		return { componentId, instanceNumber: Number(instanceNumber) };
	});
}
