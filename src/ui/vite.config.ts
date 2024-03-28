import { fileURLToPath, URL } from "url";
import { defineConfig, UserConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import monacoEditorPlugin from "vite-plugin-monaco-editor";
import streamsyncPlugin from "./viteStreamsyncPlugin";

// https://vitejs.dev/config/
export default defineConfig({
	base: "./",
	plugins: [vue(), monacoEditorPlugin({}), streamsyncPlugin()],
	includeStreamsyncComponentPath: false,
	define: {
		STREAMSYNC_LIVE_CCT: JSON.stringify("no"),
	},
	build: {
		outDir: "../streamsync/static",
		emptyOutDir: true,
	},
	resolve: {
		alias: {
			"@": fileURLToPath(new URL("./src", import.meta.url)),
		},
	},
	server: {
		proxy: {
			"/api": {
				target: "http://127.0.0.1:5000",
				ws: true,
				changeOrigin: true,
				secure: false,
				prependPath: true,
			},
			"/static": {
				target: "http://127.0.0.1:5000",
				changeOrigin: true,
				secure: false,
				prependPath: true,
			},
			"/extensions": {
				target: "http://127.0.0.1:5000",
				changeOrigin: true,
				secure: false,
				prependPath: true,
			},
		},
	},
} as UserConfig);
