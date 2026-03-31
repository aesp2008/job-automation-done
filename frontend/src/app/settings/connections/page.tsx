"use client";

import { startTransition, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  deleteGreenhouseBoards,
  deleteLeverCompanies,
  deleteRssFeedConnection,
  getIntegrationConnections,
  getProviderStatuses,
  putGreenhouseBoards,
  putLeverCompanies,
  putRssFeedConnection,
  type IntegrationConnection,
  type ProviderStatus,
} from "@/lib/api";

function splitTokens(input: string): string[] {
  return input
    .split(/[,\n]+/)
    .map((s) => s.trim().toLowerCase())
    .filter(Boolean);
}

export default function ConnectionsPage() {
  const router = useRouter();
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [connections, setConnections] = useState<IntegrationConnection[]>([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [rssUrl, setRssUrl] = useState("");
  const [greenhouseInput, setGreenhouseInput] = useState("");
  const [leverInput, setLeverInput] = useState("");

  function refresh(token: string) {
    Promise.all([getProviderStatuses(token), getIntegrationConnections(token)])
      .then(([p, c]) => {
        startTransition(() => {
          setProviders(p);
          setConnections(c);
          const rssRow = c.find((x) => x.provider === "rss_feed");
          const ru = rssRow?.config?.rss_url;
          setRssUrl(typeof ru === "string" ? ru : "");

          const gh = c.find((x) => x.provider === "greenhouse_api");
          const ght = gh?.config?.board_tokens;
          setGreenhouseInput(Array.isArray(ght) ? ght.join(", ") : "");

          const lv = c.find((x) => x.provider === "lever_api");
          const lvc = lv?.config?.companies;
          setLeverInput(Array.isArray(lvc) ? lvc.join(", ") : "");
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
      setMessage("RSS feed saved. Run “Discover all boards” on the dashboard.");
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

  async function saveGreenhouse(e: React.FormEvent) {
    e.preventDefault();
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setError("");
    setMessage("");
    const tokens = splitTokens(greenhouseInput);
    if (!tokens.length) {
      setError("Enter at least one Greenhouse board token (e.g. stripe, figma).");
      return;
    }
    try {
      await putGreenhouseBoards(token, tokens);
      setMessage("Greenhouse boards saved. Discover to pull live JSON from boards-api.greenhouse.io.");
      refresh(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  }

  async function clearGreenhouse() {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setError("");
    setMessage("");
    try {
      await deleteGreenhouseBoards(token);
      setGreenhouseInput("");
      setMessage("Greenhouse boards cleared.");
      refresh(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Remove failed");
    }
  }

  async function saveLever(e: React.FormEvent) {
    e.preventDefault();
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setError("");
    setMessage("");
    const companies = splitTokens(leverInput);
    if (!companies.length) {
      setError("Enter at least one Lever site slug (e.g. shopify, netflix).");
      return;
    }
    try {
      await putLeverCompanies(token, companies);
      setMessage("Lever sites saved. Discover to pull from api.lever.co.");
      refresh(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  }

  async function clearLever() {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setError("");
    setMessage("");
    try {
      await deleteLeverCompanies(token);
      setLeverInput("");
      setMessage("Lever sites cleared.");
      refresh(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Remove failed");
    }
  }

  return (
    <div className="flex min-h-screen items-start justify-center bg-zinc-50 py-10 dark:bg-black">
      <main className="w-full max-w-2xl rounded-xl bg-white p-8 shadow dark:bg-zinc-900">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
          Provider Connections
        </h1>
        <p className="mt-1 text-sm text-zinc-500">
          Prefer <strong>public JSON APIs</strong> (Greenhouse / Lever) or optional{" "}
          <strong>Adzuna</strong> via server env keys. RSS remains supported where sites still publish
          feeds.
        </p>

        <form className="mt-6 space-y-2 rounded border p-4" onSubmit={saveGreenhouse}>
          <h2 className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
            Greenhouse job board (tokens)
          </h2>
          <p className="text-xs text-zinc-500">
            Board token = path segment on <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-800">boards.greenhouse.io/…</code>{" "}
            (lowercase, comma-separated).
          </p>
          <input
            className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
            placeholder="stripe, figma, airbnb"
            value={greenhouseInput}
            onChange={(e) => setGreenhouseInput(e.target.value)}
          />
          <div className="flex flex-wrap gap-2">
            <button
              className="rounded bg-zinc-900 px-3 py-2 text-sm text-white dark:bg-zinc-100 dark:text-zinc-900"
              type="submit"
            >
              Save boards
            </button>
            <button className="rounded border px-3 py-2 text-sm" type="button" onClick={clearGreenhouse}>
              Clear
            </button>
          </div>
        </form>

        <form className="mt-4 space-y-2 rounded border p-4" onSubmit={saveLever}>
          <h2 className="text-sm font-medium text-zinc-900 dark:text-zinc-100">Lever postings (site slugs)</h2>
          <p className="text-xs text-zinc-500">
            Slug = subdomain on jobs.lever.co (e.g. <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-800">shopify</code>).
          </p>
          <input
            className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
            placeholder="shopify, hashicorp"
            value={leverInput}
            onChange={(e) => setLeverInput(e.target.value)}
          />
          <div className="flex flex-wrap gap-2">
            <button
              className="rounded bg-zinc-900 px-3 py-2 text-sm text-white dark:bg-zinc-100 dark:text-zinc-900"
              type="submit"
            >
              Save sites
            </button>
            <button className="rounded border px-3 py-2 text-sm" type="button" onClick={clearLever}>
              Clear
            </button>
          </div>
        </form>

        <form className="mt-4 space-y-2 rounded border p-4" onSubmit={saveRss}>
          <h2 className="text-sm font-medium text-zinc-900 dark:text-zinc-100">RSS / Atom (legacy)</h2>
          <input
            type="url"
            className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
            placeholder="https://example.com/careers/jobs.rss"
            value={rssUrl}
            onChange={(e) => setRssUrl(e.target.value)}
          />
          <div className="flex flex-wrap gap-2">
            <button className="rounded border px-3 py-2 text-sm" type="submit">
              Save feed URL
            </button>
            <button className="rounded border px-3 py-2 text-sm" type="button" onClick={clearRss}>
              Remove feed
            </button>
          </div>
        </form>

        <p className="mt-4 text-xs text-zinc-500">
          <strong>Adzuna:</strong> set <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-800">ADZUNA_APP_ID</code> and{" "}
          <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-800">ADZUNA_APP_KEY</code> in backend{" "}
          <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-800">.env</code> (see developer.adzuna.com). No UI field —
          search uses your profile target role.
        </p>

        {error ? <p className="mt-4 text-sm text-red-500">{error}</p> : null}
        {message ? <p className="mt-4 text-sm text-zinc-600 dark:text-zinc-400">{message}</p> : null}

        {connections.length ? (
          <p className="mt-4 text-xs text-zinc-500">
            Saved: {connections.map((c) => c.provider).join(", ")}
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
