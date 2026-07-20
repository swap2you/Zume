import { expect, test, type APIRequestContext, type Page } from '@playwright/test'
import path from 'node:path'

const API = 'http://127.0.0.1:8787'

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

async function requireReviewEnvironment(request: APIRequestContext) {
  const health = await request.get(`${API}/api/health`)
  expect(health.ok(), 'health').toBeTruthy()
  expect(health.headers()['x-zume-review-mode']).toBe('1')
  const healthBody = await health.json()
  expect(healthBody.review_mode, 'ENVIRONMENT MISMATCH: review_mode').toBe(true)

  const candidates = await request.get(`${API}/api/candidates`)
  expect(candidates.ok()).toBeTruthy()
  expect((await candidates.json()).items, 'ENVIRONMENT MISMATCH: candidates not empty').toEqual([])

  const facets = await request.get(`${API}/api/knowledge/facets?mode=reviewed`)
  expect(facets.ok(), 'ENVIRONMENT MISMATCH: facets').toBeTruthy()
  const counts = (await facets.json()).counts
  expect(counts.questions, 'ENVIRONMENT MISMATCH: reviewed questions').toBe(66)
  expect(counts.exercises, 'ENVIRONMENT MISMATCH: reviewed exercises').toBe(4)
  expect(counts.domains).toBeGreaterThan(0)

  const gaps = await request.get(`${API}/api/knowledge/gaps`)
  expect(gaps.ok(), 'ENVIRONMENT MISMATCH: gaps').toBeTruthy()

  const search = await request.get(
    `${API}/api/knowledge/search?q=${encodeURIComponent('What is an explicit wait in Selenium?')}&limit=5`,
  )
  expect(search.ok(), 'ENVIRONMENT MISMATCH: search').toBeTruthy()
  const payload = await search.json()
  const items = payload.items ?? payload.results ?? []
  expect(JSON.stringify(items).toLowerCase()).toContain('selenium')

  const build = await request.get(`${API}/api/build-info`)
  expect(build.ok()).toBeTruthy()
  const info = await build.json()
  expect(info.reviewed_questions).toBe(66)
  expect(info.reviewed_exercises).toBe(4)
  return info
}

async function waitForFacets(page: Page) {
  await expect(page.locator('[data-facets-ready="true"]')).toBeVisible({ timeout: 30_000 })
  const domain = page.getByRole('combobox', { name: /^Domain$/ })
  await expect.poll(async () => domain.locator('option').count(), { timeout: 30_000 }).toBeGreaterThan(1)
  return domain
}

test.beforeAll(async ({ request }) => {
  await requireReviewEnvironment(request)
}, { timeout: 180_000 })

test('review mode banner is visible', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/')
  await expect(page.getByRole('status').filter({ hasText: /Review mode/i })).toBeVisible()
  // Banner must span the top row — not steal the sidebar column and hide Overview.
  await expect(page.getByRole('heading', { name: /good work starts/i })).toBeInViewport()
})

test('reviewed library loads records from facets-driven dropdowns', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/library')
  await expect(page.getByRole('heading', { name: 'Question Library' })).toBeVisible()
  const domain = await waitForFacets(page)
  await expect(page.getByRole('combobox', { name: /^Subdomain$/ })).toBeDisabled()
  await expect(page.getByRole('combobox', { name: /^Level$/ }).locator('option')).not.toHaveCount(1)
  await expect(page.getByRole('combobox', { name: /^Priority$/ }).locator('option')).not.toHaveCount(1)
  await expect(page.getByRole('combobox', { name: /^Role track$/ }).locator('option')).not.toHaveCount(1)
  await domain.selectOption({ index: 1 })
  await expect(page.getByRole('combobox', { name: /^Subdomain$/ })).toBeEnabled()
  await expect(page.getByText(/\d+ reviewed questions/i)).toBeVisible({ timeout: 30_000 })
  await expect(page.locator('[data-question-id]').first()).toBeVisible()
  await expect(page.getByText(/^66$/).first()).toBeVisible()
})

test('library priority filter and natural-language search', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/library')
  await waitForFacets(page)
  const priority = page.getByRole('combobox', { name: /^Priority$/ })
  await expect(priority).toBeVisible()
  const options = await priority.locator('option').allTextContents()
  const p0 = options.find((text) => text.startsWith('P0'))
  if (p0) {
    await priority.selectOption({ label: p0 })
    await expect(page.getByRole('button', { name: /Priority: P0/i })).toBeVisible()
  }
  await page.getByPlaceholder(/Search questions/i).fill('What is an explicit wait in Selenium?')
  await expect(page.getByText(/\d+ reviewed questions|No reviewed questions/i)).toBeVisible({ timeout: 30_000 })
})

test('library draft and gap modes use distinct responses', async ({ page, request }) => {
  await failOnConsoleOrHttp(page)
  const reviewed = await (await request.get(`${API}/api/knowledge/facets?mode=reviewed`)).json()
  const draft = await (await request.get(`${API}/api/knowledge/facets?mode=draft`)).json()
  const gaps = await (await request.get(`${API}/api/knowledge/facets?mode=gaps`)).json()
  expect(draft.mode).toBe('draft')
  expect(gaps.gap_summary?.length ?? 0).toBeGreaterThan(0)
  expect(reviewed.counts.questions).not.toBe(draft.counts.questions)

  await page.goto('/library')
  await waitForFacets(page)
  await page.getByRole('tab', { name: 'Coverage & Gaps' }).click()
  await expect(page.getByRole('heading', { name: 'Coverage gaps' })).toBeVisible({ timeout: 30_000 })
  await expect(page.locator('.gap-table li').first()).toBeVisible()
})

test('library expands answers and uses absolute citation URLs', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/library')
  await waitForFacets(page)
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

test('builder applies distinct role policies', async ({ page, request }) => {
  await failOnConsoleOrHttp(page)

  async function preview(role: string) {
    const response = await request.post(`${API}/api/interview/preview`, {
      data: { role_track: role },
    })
    expect(response.ok(), role).toBeTruthy()
    return (await response.json()).plan
  }

  const senior = await preview('Senior SDET')
  const mobile = await preview('Mobile Automation Engineer')
  const perf = await preview('Performance Engineer')
  const ai = await preview('AI QA Engineer')
  const architect = await preview('Test Automation Architect')
  const manager = await preview('QA Manager')

  expect(senior.role_policy).toBe('senior-sdet')
  expect(mobile.role_policy).toBe('mobile-automation')
  expect(perf.role_policy).toBe('performance')
  expect(ai.role_policy).toBe('ai-qa')
  expect(architect.role_policy).toBe('automation-architect')
  expect(manager.role_policy).toBe('qa-manager')

  const seniorDomains = new Set((senior.questions ?? []).map((q: { domain?: string }) => q.domain))
  const mobileDomains = new Set((mobile.questions ?? []).map((q: { domain?: string }) => q.domain))
  const perfDomains = new Set((perf.questions ?? []).map((q: { domain?: string }) => q.domain))
  const aiDomains = new Set((ai.questions ?? []).map((q: { domain?: string }) => q.domain))
  expect([...seniorDomains]).toEqual(expect.arrayContaining(['java', 'selenium']))
  expect([...mobileDomains].join(' ')).toMatch(/mobile|appium/i)
  expect([...perfDomains].join(' ')).toMatch(/performance/i)
  expect([...aiDomains].join(' ')).toMatch(/ai|llm|agent/i)
  expect(architect.role_policy).not.toBe(senior.role_policy)
  expect(senior.knockout_question_ids).not.toEqual(manager.knockout_question_ids)
  expect(mobile.knockout_question_ids).not.toEqual(senior.knockout_question_ids)

  await page.goto('/builder')
  await page.getByRole('combobox', { name: /^Role track$/ }).selectOption('QA Manager')
  await page.getByRole('button', { name: 'Preview plan' }).click()
  await expect(page.getByText('Knockout round')).toBeVisible({ timeout: 45_000 })
  await expect(page.getByRole('strong').filter({ hasText: /QA Manager|Manager/i }).first()).toBeVisible()
})

test('intake submits fictional pasted text into review workspace', async ({ page, request }) => {
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
  const candidates = await request.get(`${API}/api/candidates`)
  const items = (await candidates.json()).items as { folder: string }[]
  expect(items.length).toBeGreaterThan(0)
  expect(items.every((item) => !/Patil_Swapnil/i.test(item.folder))).toBeTruthy()
})

test('ask retrieves a natural-language Selenium answer with local citations', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/ask')
  await page.getByLabel('Your question').fill('What is an explicit wait in Selenium?')
  await page.getByRole('button', { name: 'Ask Zume' }).click()
  await expect(page.getByText(/Confidence:/)).toBeVisible({ timeout: 30_000 })
  const citation = page.locator('a[href^="https://"]').first()
  if (await citation.count()) {
    const href = await citation.getAttribute('href')
    expect(href).not.toContain('127.0.0.1')
    expect(href?.startsWith('https://')).toBeTruthy()
  }
})

test('lab presents SQL runner', async ({ page }) => {
  await failOnConsoleOrHttp(page)
  await page.goto('/lab')
  await expect(page.getByLabel('Runner')).toContainText(/sql/i)
  await page.getByRole('button', { name: 'Run code' }).click()
  await expect(page.getByText('Exit code')).toBeVisible({ timeout: 30_000 })
})

test('settings displays doctor cards, build identity, and clear actions', async ({ page }) => {
  page.on('pageerror', (error) => { throw new Error(`pageerror: ${error.message}`) })
  page.on('console', (msg) => { if (msg.type() === 'error') throw new Error(`console error: ${msg.text()}`) })
  await page.goto('/settings')
  await expect(page.getByText('openai provider')).toBeVisible()
  await expect(page.getByText('docker labs')).toBeVisible()
  await expect(page.getByTestId('build-info')).toContainText(/66Q\/4E|v1\.0\.0/i)
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
      if (route === '/library') {
        await expect(page.locator('[data-facets-ready="true"]')).toBeVisible({ timeout: 30_000 })
      }
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2)
      expect(overflow, `${route} ${size.name} horizontal overflow`).toBeFalsy()
      await page.screenshot({
        path: path.join(testInfo.outputDir, `${size.name}${route.replaceAll('/', '-') || '-home'}.png`),
        fullPage: true,
      })
    }
  }
})
