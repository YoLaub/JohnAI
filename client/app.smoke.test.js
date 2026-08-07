import { describe, it, expect } from 'vitest';

describe('vitest/jsdom setup', () => {
  it('runs tests against a DOM environment', () => {
    document.body.innerHTML = '<div id="widgetContainer"></div>';
    expect(document.getElementById('widgetContainer')).not.toBeNull();
  });
});
