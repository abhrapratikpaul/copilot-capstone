import { test, expect } from '@playwright/test';

test.describe('Task Manager AC Verification', () => {
  // Clean all tasks before each test for isolation
  test.beforeEach(async ({ page }) => {
    // Fetch all tasks and delete each one
    const response = await page.request.get('/api/tasks');
    const tasks = await response.json();
    for (const task of tasks) {
      await page.request.delete(`/api/tasks/${task.id}`);
    }
    await page.goto('/');
  });

  test('AC-1: existing tasks displayed on page load', async ({ page }) => {
    // Seed two tasks via API
    await page.request.post('/api/tasks', {
      data: { name: 'Seeded Task A' },
      headers: { 'Content-Type': 'application/json' },
    });
    await page.request.post('/api/tasks', {
      data: { name: 'Seeded Task B' },
      headers: { 'Content-Type': 'application/json' },
    });

    // Reload to verify tasks render on page load
    await page.reload();

    const items = page.locator('#task-list li');
    await expect(items).toHaveCount(2);
    await expect(items.nth(0).locator('.task-name')).toHaveText('Seeded Task A');
    await expect(items.nth(1).locator('.task-name')).toHaveText('Seeded Task B');
  });

  test('AC-2: add a task via UI', async ({ page }) => {
    await page.fill('#task-input', 'Buy groceries');
    await page.click('#add-btn');

    const items = page.locator('#task-list li');
    await expect(items).toHaveCount(1);
    await expect(items.first().locator('.task-name')).toHaveText('Buy groceries');
  });

  test('AC-3: mark task complete shows strikethrough', async ({ page }) => {
    // Add a task
    await page.fill('#task-input', 'Finish report');
    await page.click('#add-btn');

    const item = page.locator('#task-list li').first();
    await expect(item.locator('.task-name')).toBeVisible();

    // Check the checkbox to mark complete
    await item.locator('input[type="checkbox"]').check();

    // Verify strikethrough styling on the task name
    await expect(item.locator('.task-name')).toHaveCSS(
      'text-decoration-line',
      'line-through',
    );
  });

  test('AC-4: delete a task removes it from list', async ({ page }) => {
    // Add two tasks
    await page.fill('#task-input', 'Task to keep');
    await page.click('#add-btn');
    await expect(page.locator('#task-list li')).toHaveCount(1);

    await page.fill('#task-input', 'Task to delete');
    await page.click('#add-btn');
    await expect(page.locator('#task-list li')).toHaveCount(2);

    // Delete the second task
    await page.locator('#task-list li').nth(1).locator('.delete-btn').click();

    await expect(page.locator('#task-list li')).toHaveCount(1);
    await expect(
      page.locator('#task-list li').first().locator('.task-name'),
    ).toHaveText('Task to keep');
  });

  test('AC-5: empty input validation shows error message', async ({ page }) => {
    // Click Add Task with empty input
    await page.click('#add-btn');

    await expect(page.locator('#error-message')).toHaveText(
      'Task name is required',
    );

    // Verify no task was added
    await expect(page.locator('#task-list li')).toHaveCount(0);
  });

  test('AC-6: completed tasks sort to bottom', async ({ page }) => {
    // Add three tasks
    await page.fill('#task-input', 'Alpha');
    await page.click('#add-btn');
    await expect(page.locator('#task-list li')).toHaveCount(1);

    await page.fill('#task-input', 'Beta');
    await page.click('#add-btn');
    await expect(page.locator('#task-list li')).toHaveCount(2);

    await page.fill('#task-input', 'Gamma');
    await page.click('#add-btn');
    await expect(page.locator('#task-list li')).toHaveCount(3);

    // Complete 'Alpha' — use waitForResponse to ensure re-render after sort
    const alphaItem = page.locator('#task-list li', { has: page.locator('.task-name', { hasText: 'Alpha' }) });
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/api/tasks') && resp.request().method() === 'GET'),
      alphaItem.locator('input[type="checkbox"]').check(),
    ]);

    // Wait for completed class to confirm re-render
    await expect(page.locator('#task-list li.completed')).toHaveCount(1);

    // After sort: incomplete first (Beta, Gamma), completed last (Alpha)
    const items = page.locator('#task-list li');
    await expect(items).toHaveCount(3);

    const lastItem = items.last();
    await expect(lastItem.locator('.task-name')).toHaveText('Alpha');
    await expect(lastItem).toHaveClass(/completed/);
  });

  test('AC-7: clear completed removes all completed tasks', async ({ page }) => {
    // Add tasks
    await page.fill('#task-input', 'Stay');
    await page.click('#add-btn');
    await expect(page.locator('#task-list li')).toHaveCount(1);

    await page.fill('#task-input', 'Remove Me');
    await page.click('#add-btn');
    await expect(page.locator('#task-list li')).toHaveCount(2);

    await page.fill('#task-input', 'Also Remove');
    await page.click('#add-btn');
    await expect(page.locator('#task-list li')).toHaveCount(3);

    // Complete "Remove Me" — find by text to avoid index issues after re-sort
    const removeMeItem = page.locator('#task-list li', { has: page.locator('.task-name', { hasText: 'Remove Me' }) });
    await removeMeItem.locator('input[type="checkbox"]').check();
    // After sort, "Remove Me" moves to bottom; wait for re-render
    await expect(page.locator('#task-list li')).toHaveCount(3);

    // Complete "Also Remove"
    const alsoRemoveItem = page.locator('#task-list li', { has: page.locator('.task-name', { hasText: 'Also Remove' }) });
    await alsoRemoveItem.locator('input[type="checkbox"]').check();
    await expect(page.locator('#task-list li')).toHaveCount(3);

    // Click Clear Completed
    await page.click('#clear-completed');

    // Only the incomplete task should remain
    const items = page.locator('#task-list li');
    await expect(items).toHaveCount(1);
    await expect(items.first().locator('.task-name')).toHaveText('Stay');
  });
});
