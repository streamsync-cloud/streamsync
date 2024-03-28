/**
 * Splits a flat state accessor e.g. "animals.dog" into an array ["animals", "dog"]
 * Dots can be escaped with backslash.
 *
 * @param s
 */
export function parseAccessor(s: string): string[] {
	let currentItem = "";
	const accessor = [];
	let isEscaped = false;

	// Avoided regex for speed and because Safari doesn't support negative lookbehind

	for (let i = 0; i < s.length; i++) {
		const currentChar = s[i];
		if (currentChar === "." && !isEscaped) {
			accessor.push(currentItem);
			currentItem = "";
			continue;
		}
		currentItem += currentChar;
		if (currentChar === "\\") {
			isEscaped = true;
		} else {
			isEscaped = false;
		}
	}
	accessor.push(currentItem);

	const replacedAccessor = accessor.map((s) => s.replaceAll("\\.", "."));

	return replacedAccessor;
}
