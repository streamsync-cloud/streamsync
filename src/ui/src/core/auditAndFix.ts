import {
	Component,
	ComponentMap,
	StreamsyncComponentDefinition,
} from "../streamsyncTypes";
import { getComponentDefinition } from "./templateMap";

/**
 * Audits integrity of ComponentMap. Applies automatic fixes if necessary.
 * Returns whether a fix was applied to the ComponentMap.
 *
 * @param components
 */
export function auditAndFixComponents(components: ComponentMap): boolean {
	let isFixApplied = false;
	auditOrphanComponents(components);
	Object.entries(components).forEach(([, component]) => {
		isFixApplied =
			isFixApplied || auditAndFixPositions(component, components);
		auditComponent(component);
	});
	return isFixApplied;
}

export function auditComponent(component: Component) {
	const def = getComponentDefinition(component.type);
	if (!def || def.category == "Fallback") {
		console.error(
			`Component ${component.id} (${component.type}). Invalid component type.`,
		);
		return;
	}

	fixComponentDeprecatedContent(component, def);

	auditComponentFieldKeys(component, def);
	auditComponentBinding(component, def);
}

function traverseComponentTree(
	parentId: Component["id"],
	components: ComponentMap,
	visited: Record<string, boolean> = {},
) {
	visited[parentId] = true;
	Object.entries(components)
		.filter(([, component]) => component.parentId === parentId)
		.forEach(([componentId]) =>
			traverseComponentTree(componentId, components, visited),
		);
}

function auditOrphanComponents(components: ComponentMap) {
	const visited = Object.fromEntries(
		Object.entries(components).map(([componentId]) => [componentId, false]),
	);
	traverseComponentTree("root", components, visited);
	Object.entries(visited).forEach(([componentId, isVisited]) => {
		if (!isVisited) {
			console.warn(
				`Component ${componentId} (${components[componentId].type}). Orphan component.`,
			);
		}
	});
}

function auditComponentFieldKeys(
	component: Component,
	def: StreamsyncComponentDefinition,
) {
	const fieldKeys = Object.keys(def.fields ?? {});
	if (!component.content) return;
	Object.keys(component.content).forEach((contentFieldKey) => {
		if (fieldKeys.includes(contentFieldKey)) return;
		console.warn(
			`Component ${component.id} (${component.type}). Field key "${contentFieldKey}" is defined in the component but not in the template.`,
		);
	});
}

function auditComponentBinding(
	component: Component,
	def: StreamsyncComponentDefinition,
) {
	const eventKeys = Object.keys(def.events ?? {});
	if (!component.binding) return;
	const boundEventType = component.binding.eventType;
	if (
		eventKeys.includes(boundEventType) &&
		def.events[boundEventType].bindable
	)
		return;
	console.warn(
		`Component ${component.id} (${component.type}). The component is bound to event "${component.binding.eventType}" but the template doesn't define that event or it's not bindable.`,
	);
}

/**
 * A parent with broken positions e.g. 0, 1, 4, 5 can cause problems. This function
 * finds and fixes that problem if required.
 *
 * @param component
 * @param components
 * @returns
 */
function auditAndFixPositions(
	component: Component,
	components: ComponentMap,
): boolean {
	let isFixApplied = false;
	if (component.id == "root") {
		if (component.position !== 0) {
			console.error("Root must be at position 0.");
		}
	}
	if (component.position == -1) {
		console.error(
			`Component ${component.id} (${component.type}). Invalid position.`,
		);
	}

	const positionfulChildren = Object.values(components).filter(
		(c) =>
			c.parentId === component.id &&
			c.position !== -2 &&
			!c.isCodeManaged,
	);
	let positionSum = 0;
	positionfulChildren.forEach((c) => {
		positionSum += c.position;
	});

	const arithmeticProgression =
		((positionfulChildren.length - 1) * positionfulChildren.length) / 2;
	if (arithmeticProgression !== positionSum) {
		console.error(
			`Component ${component.id} (${component.type}). Invalid children positions. Automated fix will be applied.`,
		);
		fixPositions(positionfulChildren);
		isFixApplied = true;
	}
	return isFixApplied;
}

function fixPositions(positionfulChildren: Component[]) {
	positionfulChildren.sort((a, b) => (a.position > b.position ? 1 : -1));
	positionfulChildren.map((component, index) => {
		component.position = index;
	});
}

/**
 * Corrects the mapping of deprecated properties following component changes.
 *
 * @param component
 * @param def
 */
function fixComponentDeprecatedContent(
	component: Component,
	def: StreamsyncComponentDefinition,
) {
	if (component.type == "column") {
		if ("horizontalAlignment" in component.content) {
			const mapping = {
				left: "start",
				center: "center",
				right: "end",
			};

			component.content["contentHAlign"] =
				mapping[component.content["horizontalAlignment"]] ||
				component.content["horizontalAlignment"];
			delete component.content["horizontalAlignment"];
		}
		if ("verticalAlignment" in component.content) {
			const mapping = {
				normal: "unset",
				top: "start",
				center: "center",
				bottom: "end",
			};

			component.content["contentVAlign"] =
				mapping[component.content["verticalAlignment"]] ||
				component.content["verticalAlignment"];
			delete component.content["verticalAlignment"];
		}
	} else if (component.type == "horizontalstack") {
		if ("alignment" in component.content) {
			const mapping = {
				left: "start",
				center: "center",
				right: "end",
			};

			component.content["contentHAlign"] =
				mapping[component.content["alignment"]] ||
				component.content["alignment"];
			delete component.content["alignment"];
		}
	} else if (component.type == "section") {
		if ("snapMode" in component.content) {
			delete component.content["snapMode"];
		}
	}
}
