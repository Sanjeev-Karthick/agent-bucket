export type Mode = 'keyword' | 'vector' | 'hybrid';
export interface Hit { id: string; uri: string; text: string; chunk: number; score: number }
export interface SearchResult { hits: Hit[]; mode: Mode; embedding_provider: string }
export interface Status {
  source: string; documents: number; chunks: number; embedding_provider: string; version: string;
}
export interface Job {
  id: string; status: string; indexed: number; skipped: number; deleted: number;
  error: string | null;
}

export async function api<T>(token: string, path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/v1/${path}`, {
    method: body === undefined ? 'GET' : 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  if (!response.ok) {
    throw new Error(response.status === 401 ? 'Check your access token.' : `Request failed (${response.status}).`);
  }
  return response.json() as Promise<T>;
}
