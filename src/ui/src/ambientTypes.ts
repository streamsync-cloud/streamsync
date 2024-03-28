import { StreamsyncComponentDefinition } from "./streamsyncTypes";

declare module "marked";
declare module "vue" {
	interface ComponentCustomOptions {
		streamsync?: StreamsyncComponentDefinition;
	}
}

export {};
