<template>
	<div class="CoreTabs">
		<nav
			class="tabSelector horizontal"
			data-streamsync-cage
			data-streamsync-container
		>
			<slot :instance-number="0"></slot>
		</nav>
		<div class="container">
			<slot :instance-number="1"></slot>
		</div>
	</div>
</template>

<script lang="ts">
import {
	accentColor,
	primaryTextColor,
	secondaryTextColor,
	containerBackgroundColor,
	containerShadow,
	separatorColor,
	buttonColor,
	buttonTextColor,
	buttonShadow,
	cssClasses,
} from "../../renderer/sharedStyleFields";

const description =
	"A container component for organising and displaying Tab components in a tabbed interface.";

export default {
	streamsync: {
		name: "Tab Container",
		description,
		category: "Layout",
		allowedChildrenTypes: ["tab", "repeater"],
		fields: {
			accentColor,
			primaryTextColor,
			secondaryTextColor,
			containerBackgroundColor,
			containerShadow,
			separatorColor,
			buttonColor,
			buttonTextColor,
			buttonShadow,
			cssClasses,
		},
	},
};
</script>
<script setup lang="ts">
import { inject } from "vue";
import injectionKeys from "../../injectionKeys";

const instanceData = inject(injectionKeys.instanceData);
instanceData.at(-1).value = { activeTab: undefined };
</script>

<style scoped>
@import "../../renderer/sharedStyles.css";

.CoreTabs {
	width: 100%;
}

.tabSelector {
	pointer-events: all;
	border-radius: 8px 8px 0 0;
	background: var(--containerBackgroundColor);
	display: flex;
	gap: 16px;
	width: fit-content;
	border-top: 1px solid var(--separatorColor);
	border-left: 1px solid var(--separatorColor);
	border-right: 1px solid var(--separatorColor);
	color: var(--secondaryTextColor);
	padding: 0 16px 0 16px;
	max-width: 100%;
	overflow-x: auto;
}

.childless > .tabSelector {
	display: none;
}

.container {
	border-top: 1px solid var(--separatorColor);
	border-left: 1px solid var(--separatorColor);
	border-right: 1px solid var(--separatorColor);
	border-bottom: 1px solid var(--separatorColor);
	background: var(--containerBackgroundColor);
	border-radius: 0 8px 8px 8px;
	box-shadow: var(--containerShadow);
}

.childless > .container {
	border-radius: 8px;
	border: none;
}
</style>
