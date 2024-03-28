<template>
	<div ref="rootEl" class="CoreMapbox">
		<div v-if="!fields.accessToken.value" class="noAccessTokenProvided">
			<h2>MapBox cannot be initialised.</h2>
			<h3>An access token hasn't been provided.</h3>
		</div>
		<div v-else ref="mapEl" class="map" />
		<div class="mask" />
	</div>
</template>

<script lang="ts">
import { FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const markersDefaultData = [
	{ lat: 37.79322359164316, lng: -122.39999318828129, name: "Marker" },
];

export default {
	streamsync: {
		name: "Mapbox",
		description:
			"A component to embed a Mapbox map. It can be used to display a map with markers.",
		docs: "For this component you need Mapbox access token: https://www.mapbox.com/api-documentation/#access-tokens-and-token-scopes",
		category: "Embed",
		fields: {
			accessToken: {
				name: "Access Token",
				default: "",
				desc: "Access token from Mapbox",
				type: FieldType.Text,
			},
			mapStyle: {
				name: "Map style",
				default: "mapbox://styles/mapbox/standard",
				type: FieldType.Text,
				desc: "Map style URL",
			},
			zoom: {
				name: "Zoom",
				default: "8",
				type: FieldType.Number,
			},
			lat: {
				name: "Latitude",
				default: "37.79322359164316",
				type: FieldType.Number,
			},
			lng: {
				name: "Longitude",
				default: "-122.39999318828129",
				type: FieldType.Number,
			},
			markers: {
				name: "Markers",
				init: JSON.stringify(markersDefaultData, null, 2),
				desc: "",
				type: FieldType.Object,
			},
			controls: {
				name: "Controls visible",
				default: "yes",
				type: FieldType.Text,
				options: {
					no: "No",
					yes: "Yes",
				},
				desc: "Show map controls",
			},
			cssClasses,
		},
		events: {
			"mapbox-marker-click": {
				desc: "Capture single clicks on markers.",
			},
			"mapbox-click": {
				desc: "Capture single click on map.",
			},
		},
	},
};
</script>

<script setup lang="ts">
import "mapbox-gl/dist/mapbox-gl.css";
import { inject, ref, watch, computed } from "vue";
import injectionKeys from "../../injectionKeys";
import type * as mapboxgl from "mapbox-gl";
const fields = inject(injectionKeys.evaluatedFields);
const rootEl = ref(null);
const mapEl = ref(null);
const center = computed<mapboxgl.LngLatLike>(() => [
	fields.lng.value,
	fields.lat.value,
]);
const map = ref(null);
let markers: mapboxgl.Marker[] = [];
let controls: mapboxgl.NavigationControl | null = null;

const initMap = async () => {
	if (!mapEl.value) return;
	if (!fields.accessToken.value) return;
	const mapboxgl = await import("mapbox-gl");
	try {
		// https://github.com/mapbox/mapbox-gl-js/issues/13091
		// This line is according to docs but it doesn't work
		mapboxgl.accessToken = fields.accessToken.value;
		// Following works
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		if ((mapboxgl as any).default) {
			// eslint-disable-next-line @typescript-eslint/no-explicit-any
			(mapboxgl as any).default.accessToken = fields.accessToken.value;
		}
		map.value = new mapboxgl.Map({
			container: mapEl.value,
			style: fields.mapStyle.value,
			center: center.value,
			zoom: fields.zoom.value,
		});
		map.value.on("click", (e) => {
			const event = new CustomEvent("mapbox-click", {
				detail: {
					payload: {
						lat: e.lngLat.lat,
						lng: e.lngLat.lng,
					},
				},
			});
			rootEl.value.dispatchEvent(event);
		});
		controls = new mapboxgl.NavigationControl();
		if (fields.controls.value === "yes") {
			map.value.addControl(controls);
		}
		if (fields.markers.value) {
			map.value.on("load", renderMarkers);
		}
	} catch (error) {
		// eslint-disable-next-line no-console
		console.error(error);
	}
};

const renderMarkers = async () => {
	if (!map.value) return;
	const mapboxgl = await import("mapbox-gl");
	markers.forEach((marker) => marker.remove());
	markers = [];
	fields.markers?.value?.forEach(
		(markerData: { lat: number; lng: number; name: string }) => {
			const marker = new mapboxgl.Marker()
				.setLngLat([markerData.lng, markerData.lat])
				.addTo(map.value)
				.setPopup(new mapboxgl.Popup().setText(markerData.name));
			markers.push(marker);
			marker.getElement().addEventListener("click", (e) => {
				const event = new CustomEvent("mapbox-marker-click", {
					detail: {
						payload: markerData,
					},
				});
				rootEl.value.dispatchEvent(event);
				e.stopPropagation();
			});
		},
	);
};

watch(fields.controls, () => {
	if (map.value) {
		if (fields.controls.value === "yes") {
			map.value.addControl(controls);
		} else {
			map.value.removeControl(controls);
		}
	}
});

watch(fields.markers, async () => {
	if (map.value) {
		await renderMarkers();
	}
});
watch(fields.mapStyle, () => {
	if (map.value) {
		map.value.setStyle(fields.mapStyle.value);
	}
});
watch(center, () => {
	if (map.value && center.value?.lat && center.value?.lng) {
		map.value.setCenter(center.value);
	}
});
watch(fields.zoom, () => {
	if (map.value && fields.zoom.value) {
		map.value.setZoom(fields.zoom.value);
	}
});
watch([mapEl, fields.accessToken], () => {
	initMap();
});
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreMapbox {
	position: relative;
	width: 100%;
	height: 80vh;
	background: var(--separatorColor);
}
.CoreMapbox :deep(.mapboxgl-marker) {
	cursor: pointer;
}

.noAccessTokenProvided {
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 16px;
	flex-direction: column;
}

.CoreMapbox .map {
	width: 100%;
	height: 100%;
}
.CoreMapbox .mask {
	pointer-events: none;
}

.CoreMapbox.beingEdited .mask {
	pointer-events: auto;
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
}

.CoreMapbox.beingEdited.selected .mask {
	pointer-events: none;
}
</style>
