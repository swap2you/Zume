import { expect, test } from '@playwright/test'

test('loads the workspace home', async ({ page }) => {
  const apiAvailable = await page.request.get('http://127.0.0.1:8787/api/health').then(response => response.ok()).catch(() => false)
  test.skip(!apiAvailable, 'Local Zume API is not running')
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /good work starts/i })).toBeVisible()
})
