# Custom components

It's possible to extend Streamsync with custom component templates. 

They're developed using Vue 3 and TypeScript. Once transpiled, they can be used by copying them to the `extensions/` folder of any project.

::: tip Custom components behave exactly like built-in ones
They are just as performant, can contain other components, and offer the same Builder experience. They only differ from built-in components in the way that they're bundled and imported.
:::

## Architecture

Streamsync frontend compiles to a collection of static assets that is distributed in the Python package. These static assets are then served via FastAPI.

During initialisation time, the server scans the `extensions/` folder in the project folder and looks for `.css` and `.js` files. This folder is also served, similarly to `static/`. If it finds any valid files in `extensions/`, it shares the list with clients and tells them to dynamically import these files during runtime.

_Extensions_ and _custom templates_ are currently synonyms, but this might change in order to accommodate other extension capabilities.

![Custom Components - Architecture](./images/custom-components.architecture.png)

Dependencies are [_provided_](https://vuejs.org/api/composition-api-dependency-injection.html) using injection symbols and can be _injected_ to be used by the component template. These include `evaluatedFields`, which contain the current values of the editable fields. Injected dependencies are fully typed, making  development easier.

[Rollup's `external` feature](https://rollupjs.org/configuration-options/#external), invoked via Vite, allows for extensions to be compiled without dependencies and link those during runtime. Therefore, extensions aren't bundled to be standalone, but rather to work as a piece of a puzzle.

![Custom Components - External](./images/custom-components.external.png)

## Anatomy of a template

A template defines how a certain component is rendered. For example, `corebutton` defines how _Button_ components are rendered.

Streamsync component templates are purely frontend-based. **They are Vue 3 templates that extend the Vue specification** via a [custom option](https://vuejs.org/api/utility-types.html#componentcustomoptions), `streamsync`. This _custom option_ defines all the Streamsync-specific behaviour of the component. For example, its `fields` property establishes which fields will be editable via Builder.

### Simple example

This example shows a template for _Bubble Message_, a simple demo component with one editable field, `text`.   

```vue
<template>
	<div class="BubbleMessage">
        <div class="triangle"></div>
        <div class="message">

            <!-- Shows the current value of the field "text" -->
            
            {{ fields.text.value }}
        </div>
	</div>
</template>

<script lang="ts">
export default {    
    streamsync: {
		name: "Bubble Message",
		description: "Shows a message in the shape of a speech bubble.",
		category: "Content",
		
        // Fields will be editable via Streamsync Builder
        
        fields: {
			text: {
				name: "Text",
				type: FieldType.Text,
			},
		},

        // Preview field is used in the Component Tree

		previewField: "text",
	},
};
</script>
<script setup lang="ts">
import { FieldType } from "../streamsyncTypes";
import injectionKeys from "../injectionKeys";
import { inject } from "vue";

/*
The values for the fields defined earlier in the custom option
will be available using the evaluatedFields injection symbol.
*/

const fields = inject(injectionKeys.evaluatedFields);
</script>

<style scoped>
/* ... */
</style>
```

The code above will make _Bubble Message_ available in Builder.

![Custom Components - Bubble Message](./images/custom-components.bubble-message.png)

## Developing templates

### Run a local server

To get started, clone the [Streamsync repository](https://github.com/streamsync-cloud/streamsync) from GitHub. 

To develop custom templates, at least in a developer-friendly way, you'll need a frontend development server with instant reloads.

The frontend code for Streamsync can be found in the folder `ui`. With Node and npm in your system, run `npm install` to install dependencies, and start the server with support for custom component templates using `npm run custom.dev`.

```sh
cd ui
npm install

# "custom.dev" links templates in "custom_components/"
# "dev" runs the server without them 

npm run custom.dev
```

The command above will start a frontend server, but won't be of much use by itself —a backend is needed. The frontend development server proxies backend requests to port 5000.

Start Streamsync via command line, specifying the option `--port 5000`, to provide a backend in that port. It's recommended to create a new app for testing the template you're developing.

```sh
streamsync create customtester
streamsync edit customtester --port 5000
```

You should now be able to access Streamsync via the URL provided by Vite, e.g. `http://localhost:5174`. In Builder's _Toolkit_, you should see the sample component, _Balloon Message_. Add it to your tester application.

### Create a new component

Go to `ui/src/custom_components/` and open the Vue single-file components, i.e. the `.vue` files. These files contain comments that will help you get started. Try editing the provided templates, you should see changes reflected.

::: tip
You can also have a look at the built-in component templates, since their syntax is equivalent. They can be found in the `ui/src/core_components/` folder.
:::

You can get started by duplicating one of these examples. Make sure you add the new template to the entrypoint, as discussed below.

### Define entrypoint

For custom component templates to be taken into account, they need to be accessible from the entrypoint.

Edit `ui/src/custom_components/index.ts` to define which templates you wish to export and under which identifiers.

```ts

// Import the templates

import BubbleMessage from './BubbleMessage.vue';
import BubbleMessageAdvanced from './BubbleMessageAdvanced.vue';

// Export an object with the ids and the templates as default

export default {
    "bubblemessage": BubbleMessage,
    "bubblemessageadvanced": BubbleMessageAdvanced
}
```

A single or multiple templates can be specified. Take into account that they will all be exported, and later imported, together.

## Bundling templates

### Pack and collect

Execute `npm run custom.build`, this will generate the output `.js` and `.css` files into `ui/custom_components_dist`.

```sh
# "build" builds the entire frontend
# "custom.build" only builds the custom templates 

npm run custom.build
```

Collect the files from `ui/custom_components_dist` and pack them in a folder such as `my_custom_bubbles`. 

### Try them

The folder containing the generated files, e.g. `my_custom_bubbles`, can now be placed in the `extensions/` folder of any Streamsync project. It'll be automatically detected during server startup.

### Distribute your components

You can distribute your components on pypi. For this to work, your project must contain a package whose name starts with `streamsync_` and this package must contain an ``extensions`` folder.

The template [`FabienArcellier/streamsync_bubblemessage`](https://github.com/FabienArcellier/streamsync_bubblemessage/tree/master) provides a skeleton to simply create a package without needing to understand the details of compilation.

come and promote your components on the [forum](https://github.com/streamsync-cloud/streamsync/discussions) or on [discord](https://discord.gg/sn677E3Pd3)