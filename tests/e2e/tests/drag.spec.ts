import { test, expect } from "@playwright/test";

test.describe("drag", () => {
	const COMPONENT_LOCATOR = `section.CoreSection.component`;
	const COLUMN = ".CoreColumns .CoreColumn:nth-child(1 of .CoreColumn)";
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

	test("drag and drop component into itself", async ({ page }) => {
		await page
			.locator(COMPONENT_LOCATOR)
			.dragTo(page.locator(COLUMN));
		await expect(page.locator(COLUMN)).toHaveCount(1);
		await expect(page.locator(COMPONENT_LOCATOR)).toHaveCount(1);
	});
});
