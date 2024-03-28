<template>
	<div ref="rootEl" class="CoreGoogleMaps">
		<div v-if="!fields.apiKey.value" class="noAPIKeyProvided">
			<h2>Google Maps cannot be initialised.</h2>
			<h3>An API key hasn't been provided.</h3>
		</div>
		<div v-else ref="mapEl" class="map" />
		<div class="mask" />
	</div>
</template>

<script lang="ts">
/* global google */
import { FieldType } from "../../streamsyncTypes";
import { cssClasses } from "../../renderer/sharedStyleFields";

const description =
	"A component to embed a Google Map. It can be used to display a map with markers.";

const markersDefaultData = [
	{ lat: 37.79322359164316, lng: -122.39999318828129, name: "Marker" },
];

export default {
	streamsync: {
		name: "Google Maps",
		description,
		category: "Embed",
		fields: {
			apiKey: {
				name: "API Key",
				default: "",
				desc: "API Key from Google Cloud Console.",
				type: FieldType.Text,
			},
			mapId: {
				name: "Map ID",
				default: "",
				desc: "ID of map from Google Cloud Console, needed for markers.",
				type: FieldType.Text,
			},
			mapType: {
				name: "Map type",
				type: FieldType.Text,
				default: "roadmap",
				options: {
					roadmap: "Roadmap",
					satellite: "Satellite",
					hybrid: "Hybrid",
					terrain: "Terrain",
				},
				desc: "One of 'roadmap', 'satellite', 'hybrid' or 'terrain'.",
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
				default: JSON.stringify(markersDefaultData),
				desc: "Markers data",
				type: FieldType.Object,
			},
			cssClasses,
		},
		events: {
			"gmap-marker-click": {
				desc: "Capture single clicks on markers.",
			},
			"gmap-click": {
				desc: "Capture single click on map.",
			},
		},
	},
};
</script>

<script setup lang="ts">
import { Ref, inject, ref, onMounted, watch, computed } from "vue";
import injectionKeys from "../../injectionKeys";

const rootEl: Ref<HTMLElement> = ref(null);
const mapEl: Ref<HTMLElement> = ref(null);
const fields = inject(injectionKeys.evaluatedFields);
let map: google.maps.Map | null = null;
let markers = [];

const center = computed<{ lat: number; lng: number }>(() => ({
	lat: fields.lat.value,
	lng: fields.lng.value,
}));
const mapType = computed(() =>
	["roadmap", "satellite", "hybrid", "terrain"].includes(fields.mapType.value)
		? fields.mapType.value
		: "roadmap",
);

const initMap = async () => {
	clearMarkers();
	const { Loader } = await import("@googlemaps/js-api-loader");
	const loader = new Loader({
		apiKey: fields.apiKey.value,
		version: "weekly",
	});
	await loader.load();
	map = new google.maps.Map(mapEl.value, {
		center: center.value,
		mapTypeId: mapType.value,
		zoom: 8,
		mapId: fields.mapId.value,
	});

	map.addListener("click", (e: any) => {
		const event = new CustomEvent("gmap-click", {
			detail: {
				payload: e.latLng.toJSON(),
			},
		});
		rootEl.value.dispatchEvent(event);
	});

	buildMarkers();
};

const buildMarkers = async () => {
	if (!fields.mapId.value) return;
	if (!fields.markers.value) return;
	const { AdvancedMarkerElement } = (await google.maps.importLibrary(
		"marker",
	)) as google.maps.MarkerLibrary;
	clearMarkers();
	const markersData = fields.markers.value as {
		lat: number;
		lng: number;
		name: string;
	}[];
	markersData.forEach((markerData) => {
		const marker = new AdvancedMarkerElement({
			position: {
				lat: markerData.lat,
				lng: markerData.lng,
			},
			map,
			title: markerData.name,
		});

		markers.push(marker);

		marker.addListener("click", () => {
			const event = new CustomEvent("gmap-marker-click", {
				detail: {
					payload: markerData,
				},
			});
			rootEl.value.dispatchEvent(event);
		});
	});
};

const clearMarkers = () => {
	markers.forEach((marker) => marker.setMap(null));
	markers = [];
};

onMounted(async () => {
	if (fields.apiKey.value) {
		await initMap();
	}
});
watch(center, async (newVal) => {
	if (map) {
		map.setCenter(newVal);
	}
});
watch(fields.zoom, async (newVal) => {
	if (map) {
		map.setZoom(newVal);
	}
});
watch(mapType, async (newVal) => {
	if (map) {
		map.setMapTypeId(newVal);
	}
});

watch(fields.markers, buildMarkers);
watch(fields.apiKey, initMap);
watch(fields.mapId, initMap);
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreGoogleMaps {
	position: relative;
	width: 100%;
	height: 80vh;
	background: var(--separatorColor);
}

.noAPIKeyProvided {
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 16px;
	flex-direction: column;
}

.CoreGoogleMaps .map {
	width: 100%;
	height: 100%;
	display: block;
	margin: auto;
}

.CoreGoogleMaps .mask {
	pointer-events: none;
}

.CoreGoogleMaps.beingEdited .mask {
	pointer-events: auto;
	position: absolute;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
}

.CoreGoogleMaps.beingEdited.selected .mask {
	pointer-events: none;
}
</style>
