import {categories, componentsByCategory} from "../core";

/**
 * Build the content of the sidebar which provides access to the components
 */
function componentsSidebar() {
	const sidebarHeader = [
		{
			text: 'Components',
			items: [
				{text: "Component list", link: "/components/component-list"},
			]
		}
	]

	const sidebarComponentList = categories().map((category) => {
		return {
			text: category,
			items: componentsByCategory(category).map((component) => {
				return {
					text: component.name,
					link: `/components/${component.type}`,
				};
			}),
		};
	});

	return sidebarHeader.concat(sidebarComponentList)
}

export default {
	title: "Streamsync",
	description:
		"Create data apps using a drag-and-drop UI editor, while retaining the full power of Python in the backend.",
	themeConfig: {
		logo: "/logo.svg",
		socialLinks: [
			{
				icon: "github",
				link: "https://github.com/streamsync-cloud/streamsync",
			},
			{
				icon: "discord",
				link: "https://discord.gg/sn677E3Pd3",
			},
		],
		nav: [
			{text: "Documentation", link: "/getting-started"},
			{text: "Components", link: "/components/component-list"},
		],
		sidebar: {
			'/components/': componentsSidebar(),
			'/': [
				{
					text: "Guide",
					items: [
						{text: "Getting started", link: "/getting-started"},
						{text: "Builder basics", link: "/builder-basics"},
						{text: "Application state", link: "/application-state"},
						{text: "Event handlers", link: "/event-handlers"},
						{text: "Handling inputs", link: "/handling-inputs"},
					],
				},
				{
					text: "Advanced",
					items: [
						{text: "Repeater", link: "/repeater"},
						{
							text: "Backend-initiated actions",
							link: "/backend-initiated-actions",
						},
						{text: "Page routes", link: "/page-routes"},
						{text: "Sessions", link: "/sessions"},
						{text: "Custom server", link: "/custom-server"},
						{text: "State schema", link: "/state-schema"},
						{text: "Backend-driven UI", link: "/backend-driven-ui"},
						{text: "Authentication", link: "/authentication"},
					],
				},
				{
					text: "Extending it",
					items: [
						{
							text: "Stylesheets",
							link: "/stylesheets",
						},
						{
							text: "Frontend scripts",
							link: "/frontend-scripts",
						},
						{
							text: "Custom components",
							link: "/custom-components",
						},
					],
				},
				{
					text: "Tutorials",
					items: [
						{text: "Quickstart tutorial", link: "/quickstart-tutorial"},
					]
				},
				{
					text: "Reference",
					items: [
						{text: "Testing", link: "/testing"},
						{text: "Deploy with Docker", link: "/deploy-with-docker"},
						{text: "Cloud deployment", link: "/cloud-deploy"},
						{text: "Component list", link: "/components/component-list"},
					],
				}
			]
		}
	},
	ignoreDeadLinks: 'localhostLinks',
	vite: {
		build: {
			target: "esnext",
		},
		define: {
			STREAMSYNC_LIVE_CCT: JSON.stringify("no"),
		},
	}
};
