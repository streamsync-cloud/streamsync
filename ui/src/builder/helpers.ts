
export function getClosestComponent(target: HTMLElement, selector: string): HTMLElement {
	const ignore: HTMLElement = (target as HTMLElement).closest(
		".streamsync-ignore",
	);
	if (ignore) {
		target = ignore;
	}

	return (target as HTMLElement).closest(selector);
}

