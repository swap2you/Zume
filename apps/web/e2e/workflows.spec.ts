import { expect, test, type Page } from '@playwright/test'
import path from 'node:path'

async function failOnConsoleOrHttp(page: Page) {
  page.on('pageerror', (error) => {
    throw new Error(`pageerror: ${error.message}`)
  })
  page.on('console', (msg) => {
    if (msg.type() === 'error') throw new Error(`console error: ${msg.text()}`)
  })
  page.on('response', (response) => {
    const url = response.url()
    if (url.includes('/api/') && response.status() >= 400) {
      throw new Error(`API ${response.status()} for ${url}`)
    }
  })
}

test.beforeAll(async ({ request }) => {
  const response = await request.get('http://127.0.0.1:8787/api/health').catch(() => null)
  if (!response?.ok()) throw new Error('Zume API health check failed; start the local API before running E2E tests.')
})

test('reviewed library loads records from facets-driven dropdowns', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/library')
  await expect(page.getByRole('heading', { name: 'Question Library' })).toBeVisible()
  const domain = page.getByRole('combobox', { name: /^Domain$/ })
  await expect(domain).toBeVisible()
  expect(await domain.locator('option').count()).toBeGreaterThan(1)
  await expect(page.getByRole('combobox', { name: /^Subdomain$/ })).toBeDisabled()
  await domain.selectOption({ index: 1 })
  await expect(page.getByRole('combobox', { name: /^Subdomain$/ })).toBeEnabled()
  await expect(page.getByText(/\d+ reviewed questions/i)).toBeVisible({ timeout: 30_000 })
  await expect(page.locator('[data-question-id]').first()).toBeVisible()
})

test('library priority filter and natural-language search', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/library')
  const priority = page.getByRole('combobox', { name: /^Priority$/ })
  await expect(priority).toBeVisible()
  // Prefer P0 when available; otherwise leave All.
  const options = await priority.locator('option').allTextContents()
  const p0 = options.find((text) => text.startsWith('P0'))
  if (p0) {
    await priority.selectOption({ label: p0 })
    await expect(page.getByRole('button', { name: /Priority: P0/i })).toBeVisible()
  }
  await page.getByPlaceholder(/Search questions/i).fill('What is an explicit wait in Selenium?')
  await expect(page.getByText(/\d+ reviewed questions|No reviewed questions/i)).toBeVisible({ timeout: 30_000 })
})

test('library expands answers and uses absolute citation URLs', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/library')
  const card = page.locator('[data-question-id]').first()
  await expect(card).toBeVisible({ timeout: 30_000 })
  await card.getByRole('button', { name: 'Open details' }).click()
  await expect(card.getByText('Concise answer')).toBeVisible()
  await card.getByRole('tab', { name: 'Sources' }).click()
  const link = card.locator('a[href^="https://"]').first()
  await expect(link).toBeVisible()
  const href = await link.getAttribute('href')
  expect(href?.startsWith('https://')).toBeTruthy()
})

test('practice reveals a loaded answer', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/practice')
  const reveal = page.getByRole('button', { name: 'Reveal answer' })
  await expect(reveal).toBeVisible({ timeout: 30_000 })
  await reveal.click()
  await expect(page.getByText('Suggested approach')).toBeVisible()
})

test('builder applies role policies', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/builder')
  await page.getByRole('combobox', { name: /^Role track$/ }).selectOption('QA Manager')
  await page.getByRole('button', { name: 'Preview plan' }).click()
  await expect(page.getByText('Knockout round')).toBeVisible({ timeout: 45_000 })
  await expect(page.getByRole('strong').filter({ hasText: /QA Manager|Manager/i }).first()).toBeVisible()
})

test('intake submits fictional pasted text', async ({ page }) => {
  await failOnConsoleOrHttp(page)
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

test('ask retrieves a natural-language Selenium answer', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/ask')
  await page.getByLabel('Your question').fill('What is an explicit wait in Selenium?')
  await page.getByRole('button', { name: 'Ask Zume' }).click()
  await expect(page.getByText(/Confidence:/)).toBeVisible({ timeout: 30_000 })
})

test('lab presents SQL runner', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/lab')
  await expect(page.getByLabel('Runner')).toContainText(/sql/i)
  await page.getByRole('button', { name: 'Run code' }).click()
  await expect(page.getByText('Exit code')).toBeVisible({ timeout: 30_000 })
})

test('settings displays doctor cards and clear actions', async ({ page }) => {
  page.on('pageerror', (error) => { throw new Error(`pageerror: ${error.message}`) })
  page.on('console', (msg) => { if (msg.type() === 'error') throw new Error(`console error: ${msg.text()}`) })
  await page.goto('/settings')
  await expect(page.getByText('openai provider')).toBeVisible()
  await expect(page.getByText('docker labs')).toBeVisible()
  await page.getByRole('button', { name: 'Clear Ask history' }).click()
  await expect(page.getByText(/Local data cleared|cleared/i)).toBeVisible()
})

test('every route loads at desktop and tablet', async ({ page }, testInfo) => {
  const routes = ['/', '/intake', '/finalize', '/library', '/practice', '/builder', '/lab', '/ask', '/settings']
  for (const size of [
    { name: 'desktop', width: 1440, height: 900 },
    { name: 'tablet', width: 900, height: 1200 },
  ] as const) {
    await page.setViewportSize({ width: size.width, height: size.height })
    for (const route of routes) {
      await page.goto(route)
      await expect(page.locator('main')).toBeVisible()
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2)
      expect(overflow, `${route} ${size.name} horizontal overflow`).toBeFalsy()
      await page.screenshot({
        path: path.join(testInfo.outputDir, `${size.name}${route.replaceAll('/', '-') || '-home'}.png`),
        fullPage: true,
      })
    }
  }
})
