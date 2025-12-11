export async function preloadWebSocket(): Promise<void> {
  if (typeof window === 'undefined') return;
  if ('WebSocket' in window) {
    return Promise.resolve();
  }
  await import('whatwg-fetch');
}
