import { describe, it, expect } from 'vitest';
import { escapeHtml } from './utils.js';

describe('escapeHtml', () => {
  it('escapes HTML special characters', () => {
    expect(escapeHtml('<script>alert("x")</script>')).toBe(
      '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;'
    );
  });

  it('leaves plain text untouched', () => {
    expect(escapeHtml('Bonjour JohnAi')).toBe('Bonjour JohnAi');
  });
});
