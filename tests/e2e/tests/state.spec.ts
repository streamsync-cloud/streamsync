
import { test, expect } from "@playwright/test";

const setTextField = async (page, text) => {
	await page.locator('div.CoreText.component').click();
	await page
		.locator('.BuilderFieldsText[data-key="text"] textarea')
		.fill(text);
}

const setInstruction = async (page, instruction) => {
	await page.locator('div.TestInput textarea').click();
	await page.locator('div.TestInput textarea').fill(instruction);
}

const expectTextField = async (page, text) => {
	await expect(page.locator('.TestResult .plainText')).toHaveText(text);
}

const execute = async (page) => {
	await page.locator('button.TestExec').click();
	await page.locator('button.TestExec').click();
}

test.describe("state", () => {
	let url: string;
	test.beforeAll(async ({request}) => {
		const response = await request.post(`/preset/state`);
		expect(response.ok()).toBeTruthy();
		({url} = await response.json());
	});

	test.afterAll(async ({request}) => {
		await request.delete(url);
	});

	test.beforeEach(async ({ page }) => {
		await page.goto(url);
	});

	test("increment number", async ({ page }) => {
		await setTextField(page, "@{counter}");
		await expectTextField(page, "26");
		await setInstruction(page, "state['counter'] = state['counter'] + 1");
		await execute(page);
		await expectTextField(page, "27");
	});

	test("display specific list element and replace", async ({ page }) => {
		await setTextField(page, "@{list.1}");
		await expectTextField(page, "B");
	});

	test("replace list element", async ({ page }) => {
		await setTextField(page, "@{list}");
		await expectTextField(page, '["A","B","C"]');
		await setInstruction(page, "state['list'][1] = 'X'; state['list'] = state['list']");
		await execute(page);
		await expectTextField(page, '["A","X","C"]');
	});

	test("replace whole list", async ({ page }) => {
		await setTextField(page, "@{list}");
		await expectTextField(page, '["A","B","C"]');
		await setInstruction(page, "state['list'] = ['X','Y','Z']");
		await execute(page);
		await expectTextField(page, '["X","Y","Z"]');
	});
	
	test("add to list", async ({ page }) => {
		await setTextField(page, "@{list}");
		await expectTextField(page, '["A","B","C"]');
		await setInstruction(page, "state['list'].append('D'); state['list'] = state['list']");
		await execute(page);
		await expectTextField(page, '["A","B","C","D"]');
	});

	test("remove from list", async ({ page }) => {
		await setTextField(page, "@{list}");
		await expectTextField(page, '["A","B","C"]');
		await setInstruction(page, "state['list'].pop(); state['list'] = state['list']");
		await execute(page);
		await expectTextField(page, '["A","B"]');
	});

	test("add to dict", async ({ page }) => {
		await setTextField(page, "@{dict}");
		await expectTextField(page, '{"a":1,"b":2}');
		await setInstruction(page, "state['dict']['c'] = 3");
		await execute(page);
		await expectTextField(page, '{"a":1,"b":2,"c":3}');
	});

	test("remove from dict", async ({ page }) => {
		await setTextField(page, "@{dict}");
		await expectTextField(page, '{"a":1,"b":2}');
		await setInstruction(page, "del state['dict']['b']; state['dict'] = state['dict']");
		await execute(page);
		await expectTextField(page, '{"a":1}');
	});

	test("replace dict deeply nested value", async ({ page }) => {
		await setTextField(page, "@{nested.c.e}");
		await expectTextField(page, "4");
		await setInstruction(page, "state['nested']['c']['e'] = 'some text'");
		await execute(page);
		await expectTextField(page, "some text");
	});

	test("add to deeply nested dict", async ({ page }) => {
		await setTextField(page, "@{nested}");
		await expectTextField(page, '{"a":1,"b":2,"c":{"d":3,"e":4}}');
		await setInstruction(page, "state['nested']['c']['f'] = 'some text'");
		await execute(page);
		await expectTextField(page, '{"a":1,"b":2,"c":{"d":3,"e":4,"f":"some text"}}');
	});

	test(" remove from deeply nested dict", async ({ page }) => {
		await setTextField(page, "@{nested}");
		await expectTextField(page, '{"a":1,"b":2,"c":{"d":3,"e":4}}');
		await setInstruction(page, "del state['nested']['c']['e']; state['nested']['c'] = state['nested']['c']");
		await execute(page);
		await expectTextField(page, '{"a":1,"b":2,"c":{"d":3}}');
	});
});
