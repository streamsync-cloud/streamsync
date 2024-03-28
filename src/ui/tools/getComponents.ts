import { generateCore } from "../src/core";
const ss = generateCore();
const types = ss.getSupportedComponentTypes();
const data = types.map((type) => {
	const def = ss.getComponentDefinition(type);
	return { type, ...def };
});
export { data };
