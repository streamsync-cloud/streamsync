import { registerComponentTemplate } from "./templateMap";

const CUSTOM_COMPONENTS_GLOBAL_VAR = "StreamsyncCustomComponentTemplates";

export async function loadExtensions(extensionPaths: string[]) {
	await Promise.all(
		extensionPaths.map(async (path) => {
			const lcPath = path.toLocaleLowerCase();
			if (lcPath.endsWith(".js")) {
				await importCustomComponentTemplate(path);
			} else if (lcPath.endsWith(".css")) {
				loadStylesheet(path);
			}
		}),
	);
}

async function importCustomComponentTemplate(path: string) {
	console.log(`Importing custom component templates at "${path}"...`);
	await import(/* @vite-ignore */ getRelativeExtensionsPath() + path);
	Object.entries(window[CUSTOM_COMPONENTS_GLOBAL_VAR])?.forEach(
		([key, template]) => {
			console.log(`Registering template for "${key}".`);
			registerComponentTemplate(`custom_${key}`, template);
		},
	);
}

function loadStylesheet(path: string) {
	const el: HTMLLinkElement = document.createElement("link");
	el.rel = "stylesheet";
	el.href = getRelativeExtensionsPath() + path;
	document.head.appendChild(el);
}

function getRelativeExtensionsPath() {
	let pathname = window.location.pathname;
	if (!pathname.endsWith("/")) {
		pathname += "/";
	}

	return `${pathname}extensions/`;
}
