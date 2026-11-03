import { afterEach, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import App from './App';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

it('requires authentication and explains rejected tokens', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 401 }));
  render(<App />);
  expect(screen.queryByRole('button', { name: /Sync source/ })).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText('Access token'), { target: { value: 'wrong-token' } });
  fireEvent.click(screen.getByRole('button', { name: /Open console/ }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Check your access token.');
});

it('connects and makes the demo limitation visible', async () => {
  vi.stubGlobal('fetch', vi.fn().mockImplementation((url: string) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(url.endsWith('/jobs') ? [] : {
      source: 'demo', documents: 0, chunks: 0, embedding_provider: 'hash', version: '0.1.0a1',
    }),
  })));
  render(<App />);
  fireEvent.change(screen.getByLabelText('Access token'), { target: { value: 'local-demo-token-change-me' } });
  fireEvent.click(screen.getByRole('button', { name: /Open console/ }));
  expect(await screen.findByText(/hash vectors are lexical fixtures/)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Sync source/ })).toBeInTheDocument();
});
