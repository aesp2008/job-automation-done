"use client";

import { startTransition, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  deleteRssFeedConnection,
  getIntegrationConnections,
  getProviderStatuses,
  putRssFeedConnection,
  type IntegrationConnection,
  type ProviderStatus,
} from "@/lib/api";

export default function ConnectionsPage() {
  const router = useRouter();
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [connections, setConnections] = useState<IntegrationConnection[]>([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [rssUrl, setRssUrl] = useState("");

  function refresh(token: string) {
    Promise.all([getProviderStatuses(token), getIntegrationConnections(token)])
      .then(([p, c]) => {
        startTransition(() => {
          setProviders(p);
          setConnections(c);
          const row = c.find((x) => x.provider === "rss_feed");
          const u = row?.config?.rss_url;
          setRssUrl(typeof u === "string" ? u : "");
        });
      })
      .catch(() => {
        setError("Unable to load integrations.");
      });
  }

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.replace("/");
      return;
    }
    refresh(token);
  }, [router]);

  async function saveRss(e: React.FormEvent) {
    e.preventDefault();
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setError("");
    setMessage("");
    if (!rssUrl.trim()) {
      setError("Enter a feed URL or use Remove feed.");
      return;
    }
    try {
      await putRssFeedConnection(token, rssUrl.trim());
      setMessage("RSS feed saved. Run “Discover all boards” on the dashboard to import postings.");
      refresh(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  }

  async function clearRss() {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setError("");
    setMessage("");
    try {
      await deleteRssFeedConnection(token);
      setRssUrl("");
      setMessage("RSS feed removed.");
      refresh(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Remove failed");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
      <main className="w-full max-w-2xl rounded-xl bg-white p-8 shadow dark:bg-zinc-900">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
          Provider Connections
        </h1>
        <p className="mt-1 text-sm text-zinc-500">
          Stubs show status below. RSS feeds are live: paste a public Atom/RSS jobs URL to ingest
          listings on the next discovery run.
        </p>

        <form className="mt-6 space-y-2 rounded border p-4" onSubmit={saveRss}>
          <h2 className="text-sm font-medium text-zinc-900 dark:text-zinc-100">RSS / Atom job feed</h2>
          <input
            type="url"
            className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
            placeholder="https://example.com/careers/jobs.rss"
            value={rssUrl}
            onChange={(e) => setRssUrl(e.target.value)}
          />
          <div className="flex flex-wrap gap-2">
            <button className="rounded bg-zinc-900 px-3 py-2 text-sm text-white dark:bg-zinc-100 dark:text-zinc-900" type="submit">
              Save feed URL
            </button>
            <button className="rounded border px-3 py-2 text-sm" type="button" onClick={clearRss}>
              Remove feed
            </button>
          </div>
        </form>

        {error ? <p className="mt-4 text-sm text-red-500">{error}</p> : null}
        {message ? <p className="mt-4 text-sm text-zinc-600 dark:text-zinc-400">{message}</p> : null}

        {connections.length ? (
          <p className="mt-4 text-xs text-zinc-500">
            Saved connections: {connections.map((c) => c.provider).join(", ")}
          </p>
        ) : null}

        <div className="mt-5 space-y-3">
          {providers.map((provider) => (
            <div key={provider.provider} className="rounded border p-3">
              <p className="font-medium capitalize">{provider.provider.replace(/_/g, " ")}</p>
              <p className="text-sm text-zinc-500">
                Status: {provider.connected ? "Connected" : "Not connected"} | Mode: {provider.mode}
              </p>
              <p className="mt-1 text-sm text-zinc-500">{provider.details}</p>
            </div>
          ))}
        </div>

        <button
          className="mt-6 rounded border px-4 py-2 text-sm"
          type="button"
          onClick={() => router.push("/dashboard")}
        >
          Back to Dashboard
        </button>
      </main>
    </div>
  );
}
