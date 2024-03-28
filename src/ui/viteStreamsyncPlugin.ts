import { ResolvedConfig, Plugin } from "vite";

type StreamsyncPluginConfig = ResolvedConfig & {
	includeStreamsyncComponentPath?: boolean;
};

export default (): Plugin => {
	let config: StreamsyncPluginConfig;

	return {
		name: "streamsync-plugin",
		configResolved(resolvedConfig) {
			config = resolvedConfig as StreamsyncPluginConfig;
		},
		transform(code: string, id: string) {
			if (/vue&type=docs/.test(id)) {
				const docs = code
					.replaceAll(/'/g, "\\'")
					.replaceAll(/\n/g, "\\n")
					.replaceAll(/\r/g, "\\r")
					.trim()
					.replace(/^(\\n|\\t|[ \s])*/, "")
					.replace(/(\\n|\\t|[ \s])*$/, "");
				return `export default Comp => {
					if(!Comp.streamsync) return;
					Comp.streamsync.docs = '${docs}';
				}`;
			}
			if (/\.vue$/.test(id)) {
				if (config.includeStreamsyncComponentPath === false) return;
				const fileRef = id.replace(__dirname, "");
				return `${code}
					if(_sfc_main.streamsync) _sfc_main.streamsync.fileRef = '${fileRef}';
				`;
			}
		},
	};
};
