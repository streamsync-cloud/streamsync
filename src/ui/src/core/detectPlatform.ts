function getPlatform() {
	const platform: string =
		navigator?.userAgentData?.platform || navigator?.platform;
	return platform;
}

export function isPlatformMac() {
	const platform = getPlatform();
	if (platform.toLowerCase().indexOf("mac") != -1) return true;
	return false;
}
