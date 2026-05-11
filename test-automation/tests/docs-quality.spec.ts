import { test, expect } from '@playwright/test';
import * as fs from 'fs/promises';
import * as path from 'path';

/**
 * Document quality verification tests.
 * These tests verify that SDLC documents meet quality standards.
 */

const REPO_ROOT = path.resolve(__dirname, '../..');

test.describe('SDLC Document Quality', () => {
  test('requirements.md exists and has required sections', async () => {
    const filePath = path.join(REPO_ROOT, 'requirements.md');
    const content = await fs.readFile(filePath, 'utf-8');
    
    expect(content).toContain('# Requirements');
    expect(content).toContain('## Functional Requirements');
    expect(content).toContain('## Acceptance Criteria');
  });

  test('architecture.md exists and has required sections', async () => {
    const filePath = path.join(REPO_ROOT, 'architecture.md');
    const content = await fs.readFile(filePath, 'utf-8');
    
    expect(content).toContain('# Architecture');
    expect(content).toContain('## Goals');
    expect(content).toContain('## Proposed Solution');
  });

  test('design-review.md exists and has required sections', async () => {
    const filePath = path.join(REPO_ROOT, 'design-review.md');
    const content = await fs.readFile(filePath, 'utf-8');
    
    expect(content).toContain('# Design Review');
    expect(content).toContain('## Meta');
    expect(content).toContain('## Summary');
  });

  test('impl-plan.md exists and has required sections', async () => {
    const filePath = path.join(REPO_ROOT, 'impl-plan.md');
    const content = await fs.readFile(filePath, 'utf-8');
    
    expect(content).toContain('# Implementation Plan');
    expect(content).toContain('## Implementation Steps');
  });
});
