import { expect, test } from '@playwright/test'

test.beforeAll(async ({ request }) => {
  const response = await request.get('http://127.0.0.1:8787/api/health').catch(() => null)
  if (!response?.ok()) throw new Error('Zume API health check failed; start the local API before running E2E tests.')
})

test('library searches and filters P0', async ({ page }) => {
  await page.goto('/library')
  await page.getByLabel('Priority').selectOption('P0')
  await page.getByLabel('Search').fill('test')
  await expect(page.getByText(/results · page/i)).toBeVisible()
})

test('practice reveals a loaded answer', async ({ page }) => {
  await page.goto('/practice')
  const reveal = page.getByRole('button', { name: 'Reveal answer' })
  await expect(reveal).toBeVisible()
  await reveal.click()
  await expect(page.getByText('Suggested approach')).toBeVisible()
})

test('builder previews an interview plan', async ({ page }) => {
  await page.goto('/builder')
  await page.getByRole('button', { name: 'Preview plan' }).click()
  await expect(page.getByText('Knockout round')).toBeVisible({ timeout: 45_000 })
})

test('intake submits fictional pasted text', async ({ page }) => {
  await page.goto('/intake')
  await page.getByLabel('Resume text').fill(
    [
      'Fictional Candidate',
      'Senior SDET',
      '8 years Java Selenium TestNG Rest Assured SQL CI/CD experience',
      'Built Selenium frameworks, API contract tests, and CI pipelines.',
    ].join('\n'),
  )
  await page.getByRole('button', { name: 'Build pre-interview package' }).click()
  await expect(page.getByText('Screening decision')).toBeVisible({ timeout: 90_000 })
})

test('ask displays citations when returned', async ({ page }) => {
  await page.goto('/ask')
  await page.getByLabel('Your question').fill('What is a contract test?')
  await page.getByRole('button', { name: 'Ask Zume' }).click()
  await expect(page.getByText(/Confidence:/)).toBeVisible({ timeout: 30_000 })
})

test('lab presents SQL runner', async ({ page }) => {
  await page.goto('/lab')
  await expect(page.getByLabel('Runner')).toContainText(/sql/i)
})

test('settings displays doctor cards', async ({ page }) => {
  await page.goto('/settings')
  await expect(page.getByText('openai provider')).toBeVisible()
  await expect(page.getByText('docker labs')).toBeVisible()
})
