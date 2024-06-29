import { test, expect } from "@playwright/test";
import components from "writer-ui/components.codegen.json";

type Component = {
	type: string;
	allowedParentTypes?: string[];
};

type ComponentTestData = {
	type: string;
	test: string;
	locator: string;
	ignore?: boolean;
	allowedParentTypes?: string[];
};

const mapComponents = {
	root: {ignore: true},
	page: {ignore: true},
	column: {ignore: true},
	tab: {ignore: true},
	step: {ignore: true},
	dropdowninput: {locator: '.component.wf-type-dropdowninput label'},
	section: {test: 'basic'},
	columns: {test: 'basic'},
	sidebar: {test: 'basic'},
	fileinput: {locator: '.component.wf-type-fileinput label'},
	dateinput: {locator: '.component.wf-type-dateinput label'},
	timeinput: {locator: '.component.wf-type-timeinput label'},
	sliderinput: {locator: '.component.wf-type-sliderinput label'},
	numberinput: {locator: '.component.wf-type-numberinput label'},
	textinput: {locator: '.component.wf-type-textinput label'},
}

function findTest(component: Component) {
	if(!component.allowedParentTypes || component.allowedParentTypes?.includes('column')) {
		return 'full';
	}
	if(!component.allowedParentTypes || component.allowedParentTypes?.includes('page')) {
		return 'basic';
	}
	return 'none';
}

const tests = components
	.map((component: Component): ComponentTestData => ({
		...component, 
		test: findTest(component),
		locator: '.component.wf-type-' + component.type,
		...(mapComponents[component.type] || {}),
	}))

tests
	.filter((component: ComponentTestData) => !component.ignore)
	.forEach((component: ComponentTestData) => {
		switch(component.test) {
			case 'basic':
				basicTest(component);
				break;
			case 'full':
				fullTest(component);
				break;
			default:
				failTest(component);
		}
	});

function failTest({type}: ComponentTestData) {
	test.describe(type, () => {
		test("tests are not implemented", async () => {
			expect(true).toBeFalsy();
		});
	});
}


function fullTest({type, locator}: ComponentTestData) {
	test.describe(type, () => {
		const TYPE = type;
		const COMPONENT_LOCATOR = locator;
		const COLUMN1 = ".CoreColumns .CoreColumn:nth-child(1 of .CoreColumn)";
		const COLUMN2 = ".CoreColumns .CoreColumn:nth-child(2 of .CoreColumn)";
		let url: string;

		test.beforeAll(async ({request}) => {
			const response = await request.post(`/preset/2columns`);
			expect(response.ok()).toBeTruthy();
			({url} = await response.json());
		});

		test.afterAll(async ({request}) => {
			await request.delete(url);
		});

		test.beforeEach(async ({ page }) => {
			await page.goto(url);
		});

		test("create, drag and drop and remove", async ({ page }) => {
			await page
				.locator(`div.component.button[data-component-type="${TYPE}"]`)
				.dragTo(page.locator(COLUMN1));
			await expect(
				page.locator(COLUMN1 + " " + COMPONENT_LOCATOR),
			).toHaveCount(1);
			await expect(
				page.locator(COLUMN2 + " " + COMPONENT_LOCATOR),
			).toHaveCount(0);

			await page.locator(COMPONENT_LOCATOR).dragTo(page.locator(COLUMN2));
			await expect(
				page.locator(COLUMN1 + " " + COMPONENT_LOCATOR),
			).toHaveCount(0);
			await expect(
				page.locator(COLUMN2 + " " + COMPONENT_LOCATOR),
			).toHaveCount(1);

			await page.locator(COMPONENT_LOCATOR).click();
			await page
				.locator(
					'.BuilderComponentShortcuts .actionButton[data-automation-action="delete"]',
				)
				.click();
			await expect(page.locator(COMPONENT_LOCATOR)).not.toBeVisible();
			await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0);
		});
	});
}

function basicTest({type, locator}: ComponentTestData) {
	test.describe(type, () => {
		const TYPE = type;
		const COMPONENT_LOCATOR = locator;
		const TARGET = ".CorePage";
		let url: string;

		test.beforeAll(async ({request}) => {
			const response = await request.post(`/preset/empty_page`);
			expect(response.ok()).toBeTruthy();
			({url} = await response.json());
		});

		test.afterAll(async ({request}) => {
			await request.delete(url);
		});

		test.beforeEach(async ({ page }) => {
			await page.goto(url);
		});

		test("create and remove", async ({ page }) => {
			await page
				.locator(`div.component.button[data-component-type="${TYPE}"]`)
				.dragTo(page.locator(TARGET));
			await expect(
				page.locator(TARGET + " " + COMPONENT_LOCATOR),
			).toHaveCount(1);

			await page.locator(COMPONENT_LOCATOR).click();
			await page
				.locator(
					'.BuilderComponentShortcuts .actionButton[data-automation-action="delete"]',
				)
				.click();
			await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(0);
		});
	});
}
