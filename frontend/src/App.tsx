import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { api, type Job, type Mode, type SearchResult, type Status } from './api';

export default function App() {
  const [token, setToken] = useState('');
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState<Status | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [query, setQuery] = useState('How do I rotate access keys?');
  const [mode, setMode] = useState<Mode>('hybrid');
  const [result, setResult] = useState<SearchResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    const [nextStatus, nextJobs] = await Promise.all([
      api<Status>(token, 'status'), api<Job[]>(token, 'jobs'),
    ]);
    setStatus(nextStatus);
    setJobs(nextJobs);
  }, [token]);

  useEffect(() => {
    if (!connected) return;
    const interval = window.setInterval(() => { void refresh().catch(() => setError('Connection interrupted.')); }, 2000);
    return () => window.clearInterval(interval);
  }, [connected, refresh]);

  async function connect(event: FormEvent) {
    event.preventDefault();
    setError('');
    try { await refresh(); setConnected(true); }
    catch (failure) { setError((failure as Error).message); }
  }

  async function sync() {
    setBusy(true); setError('');
    try { await api<Job>(token, 'sync', {}); await refresh(); }
    catch (failure) { setError((failure as Error).message); }
    finally { setBusy(false); }
  }

  async function search(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('');
    try { setResult(await api<SearchResult>(token, 'search', { query, mode, limit: 5 })); }
    catch (failure) { setError((failure as Error).message); }
    finally { setBusy(false); }
  }

  return <div className="shell">
    <header><a className="brand" href="/">ab<span>agent-bucket</span></a><span className="pill">V0.1 · developer preview</span></header>
    <main>
      <div className="eyebrow">YOUR BUCKET. YOUR CONTEXT.</div>
      <h1>Object storage,<br /><span>agent ready.</span></h1>
      <p className="intro">Search the knowledge you already store. Find source-backed context for your next agent workflow.</p>
      {!connected ? <form className="panel connect" onSubmit={event => void connect(event)}>
        <h2>Connect to your sidecar</h2>
        <label htmlFor="token">Access token</label>
        <input id="token" type="password" value={token} onChange={event => setToken(event.target.value)} required autoComplete="off" />
        <p className="muted">Use AB_API_TOKEN from your configuration. The token stays in this tab’s memory.</p>
        <button type="submit">Open console →</button>
      </form> : <>
        <section className="stats" aria-label="Index status">
          <div><span>Source</span><strong>{status?.source}</strong></div>
          <div><span>Documents</span><strong>{status?.documents ?? 0}</strong></div>
          <div><span>Chunks</span><strong>{status?.chunks ?? 0}</strong></div>
          <button onClick={() => void sync()} disabled={busy}>Sync source ↻</button>
        </section>
        {status?.embedding_provider === 'hash' && <p className="notice">Offline demo mode: hash vectors are lexical fixtures. Enable FastEmbed for semantic retrieval.</p>}
        <section className="panel">
          <div className="section-title"><h2>Explore your context</h2><span className="muted">REST + MCP</span></div>
          <form onSubmit={event => void search(event)}>
            <label htmlFor="query">Search your documents</label>
            <div className="search-row">
              <input id="query" value={query} onChange={event => setQuery(event.target.value)} required maxLength={2000} />
              <select aria-label="Search mode" value={mode} onChange={event => setMode(event.target.value as Mode)}>
                <option value="hybrid">Hybrid</option><option value="keyword">Keyword</option><option value="vector">Vector</option>
              </select>
              <button disabled={busy} type="submit">{busy ? 'Working…' : 'Search →'}</button>
            </div>
          </form>
          <div aria-live="polite">
            {result === null && <p className="empty">Sync your source, then ask your first question.</p>}
            {result?.hits.length === 0 && <p className="empty">No matching chunks. Sync your source or try another query.</p>}
            {result?.hits.map(hit => <article className="hit" key={hit.id}>
              <div><code>{hit.uri}</code><span className="muted">chunk {hit.chunk} · {hit.score.toFixed(3)}</span></div>
              <p>{hit.text}</p>
            </article>)}
          </div>
        </section>
        <section className="panel"><h2>Recent syncs</h2>
          {!jobs.length && <p className="muted">No syncs yet.</p>}
          {jobs.slice(0, 5).map(job => <div className="job" key={job.id}>
            <span className={`job-status ${job.status}`}>{job.status}</span>
            <span>{job.indexed} indexed · {job.skipped} unchanged / unsupported · {job.deleted} removed</span>
            {job.error && <p role="alert">{job.error}</p>}
          </div>)}
        </section>
        <button className="quiet" onClick={() => { setConnected(false); setToken(''); setResult(null); }}>Disconnect</button>
      </>}
      {error && <p role="alert" className="error">{error}</p>}
    </main>
    <footer><span>Single-node first, scale-out by design.</span><a href="https://github.com/Sanjeev-Karthick/agent-bucket">Source & documentation ↗</a></footer>
  </div>;
}
