import { test, expect } from "@playwright/test";
import components from "streamsync-ui/components.json";

const setInstruction = async (page, instruction) => {
	await page.locator('div.TestInput textarea').click();
	await page.locator('div.TestInput textarea').fill(instruction);
}

const execute = async (page) => {
	await page.locator('button.TestExec').click();
	await page.locator('button.TestExec').click();
}


function generateValue(key, field) {
	if (field.type === "Text") {
		if(key === 'icon') {
			return 'error-warning';
		}
		if (field.options) {
			return Object.keys(field.options)[0];
		}
		
		return "TEST_STRING";
	} else if (field.type === "Number") {
		return "7357";
	} else if (field.type === "Color") {
		return "#007357";
	} else if (field.type === "array") {
		return [];
	} else {
		return null;
	}
}

function generateValues(fields) {
	const values = {};
	Object.entries(fields).forEach(([key, field]) => {
		const v =  generateValue(key, field);
		if (v !== null) {
			values[key] = v;
		}
	});
	return values;
}


test.describe("low-code UI", () => {
	let url: string;
	test.beforeAll(async ({request}) => {
		const response = await request.post(`/preset/low_code`);
		expect(response.ok()).toBeTruthy();
		({url} = await response.json());
	});

	test.afterAll(async ({request}) => {
		await request.delete(url);
	});

	test.beforeEach(async ({ page }) => {
		await page.goto(url);
	});

	test("init_ui -  ui initialization" , async ({ page }) => {
			await expect(page.locator(`.initialization .ss-type-text`)).toHaveText("Initialization successful!");
	});

	components.forEach(({ type, name, fields, allowedParentTypes }) => {
		const renderError = type === 'root' || (allowedParentTypes && !allowedParentTypes.includes('section'));
		const componentName = name.replaceAll(/\s/g, "");
		test(`create ${type} with ui.${componentName}() inside of section ${renderError ? '- render error' : ''}`, async ({ page }) => {
			const props = generateValues(fields);
			await setInstruction(page, `
with ui.find('results'):
		ui.${componentName}(${JSON.stringify(props)})
			`);
			await execute(page);
			await expect(page.locator(`.results .ss-type-${type}.component`)).toHaveCount(1);

			await page.locator(`.results .ss-type-${type}.component`).click({force: true});
			for (const [key, value] of Object.entries(props)) {
				await expect(page.locator(`.BuilderSettings div[data-key="${key}"] input, .BuilderSettings div[data-key="${key}"] textarea`)).toHaveCount(1);
				await expect(page.locator(`.BuilderSettings div[data-key="${key}"] input, .BuilderSettings div[data-key="${key}"] textarea`)).toHaveValue(value);
			}

			if (renderError) {
				await expect(page.locator(`.results .ss-type-${type}.component`)).toHaveClass(/RenderError/);
			}else{
				await expect(page.locator(`.results .ss-type-${type}.component`)).not.toHaveClass(/RenderError/);
			}
		});
	});
	test("settings should be enabled for bmc", async ({ page }) => {
			await page.locator(`.results`).click({force: true});
			await expect(page.locator(`.BuilderSettings > .sections`)).not.toHaveAttribute("inert");
			await expect(page.locator(`.BuilderSettings > .cmc-warning`)).toHaveCount(0);
	});

	test("settings should be disabled for cmc", async ({ page }) => {
			await setInstruction(page, `
with ui.find('results'):
			ui.Text({"cssClasses": "out", "text": "Hello"})
			`);
			await execute(page);
			await page.locator(`.results .ss-type-text.component.out`).click({force: true});
			await expect(page.locator(`.BuilderSettings > .sections`)).toHaveAttribute("inert");
			await expect(page.locator(`.BuilderSettings > .cmc-warning`)).toHaveCount(1);
	});

	test("create nested components", async ({ page }) => {
			await setInstruction(page, `
with ui.find('results'):
	with ui.ColumnContainer({"cssClasses": "level1"}):
		with ui.Column({"cssClasses": "level2"}):
			ui.Text({"cssClasses": "level3", "text": "Hello"})
			`);
			await execute(page);
			await expect(page.locator(`.results .ss-type-columns.level1 .ss-type-column.level2 .ss-type-text.level3`)).toHaveCount(1);
			await expect(page.locator(`.results .ss-type-columns.level1 .ss-type-column.level2 .ss-type-text.level3`)).toHaveText("Hello");
	});

	test("binding state", async ({ page }) => {
			await setInstruction(page, `
with ui.find('results'):
	ui.TextInput({"cssClasses": "in"}, binding={"ss-change": "value"})
	ui.Text({"cssClasses": "out", "text": "@{value}"})
			`);
			await execute(page);
			await page.locator(`.results .in input`).fill("Hello");
			await expect(page.locator(`.results .out`)).toHaveText("Hello");
	});

	test("visibility", async ({ page }) => {
			await setInstruction(page, `
with ui.find('results'):
	ui.Text({"cssClasses": "out", "text": "Hello"}, visible="no")
			`);
			await execute(page);
			await expect(page.locator(`.results .out`)).toBeHidden();
	});

	test("handlers", async ({ page }) => {
			await setInstruction(page, `
with ui.find('results'):
	ui.TextInput({"cssClasses": "in"}, handlers={"ss-change": update_value})
	ui.Text({"cssClasses": "out", "text": "@{value}"})
			`);
			await execute(page);
			await page.locator(`.results .in input`).fill("Hello");
			await expect(page.locator(`.results .out`)).toHaveText("Hello");
	});
});
