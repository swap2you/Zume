import { expect, test } from '@playwright/test'

test.beforeAll(async ({ request }) => {
  const response = await request.get('http://127.0.0.1:8787/api/health').catch(() => null)
  if (!response?.ok()) throw new Error('Zume API health check failed; start the local API before running E2E tests.')
})

test('loads the workspace home', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /good work starts/i })).toBeVisible()
})

test('uses tablet navigation', async ({ page }) => {
  await page.setViewportSize({ width: 768, height: 1024 })
  await page.goto('/')
  await expect(page.getByRole('navigation', { name: 'Primary navigation' })).toBeVisible()
  await page.getByRole('link', { name: 'Question library' }).click()
  await expect(page.getByRole('heading', { name: 'Question library' })).toBeVisible()
})
