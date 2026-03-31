"use client";

import { startTransition, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getIntegrationConnections, getProviderStatuses, type IntegrationConnection, type ProviderStatus } from "@/lib/api";

export default function ConnectionsPage() {
  const router = useRouter();
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [connections, setConnections] = useState<IntegrationConnection[]>([]);

  function refresh(token: string) {
    Promise.all([getProviderStatuses(token), getIntegrationConnections(token)])
      .then(([p, c]) => {
        startTransition(() => {
          setProviders(p);
          setConnections(c);
        });
      })
      .catch(() => {});
  }

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.replace("/");
      return;
    }
    refresh(token);
  }, [router]);

  return (
    <div className="flex min-h-screen items-start justify-center bg-zinc-50 py-10 dark:bg-black">
      <main className="w-full max-w-2xl rounded-xl bg-white p-8 shadow dark:bg-zinc-900">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">LinkedIn</h1>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          This project is <strong>LinkedIn-first</strong>. There is no public paste-and-fetch URL for your personalized
          LinkedIn job feed (unlike some ATS boards). Real listings require a{" "}
          <a
            className="text-blue-600 underline dark:text-blue-400"
            href="https://www.linkedin.com/developers/"
            target="_blank"
            rel="noreferrer"
          >
            LinkedIn Developer
          </a>{" "}
          application, OAuth sign-in, and API products your use case is allowed to use—all subject to LinkedIn&apos;s
          terms.
        </p>
        <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
          Today the backend exposes one <strong>stub</strong> listing so you can try matching, resume tailoring, and manual
          apply flows. Use <strong>Discover LinkedIn (stub)</strong> on the dashboard after setting target roles in
          Preferences.
        </p>

        {connections.length ? (
          <p className="mt-6 text-xs text-zinc-500">
            Stored connections (future OAuth): {connections.map((c) => c.provider).join(", ") || "—"}
          </p>
        ) : null}

        <div className="mt-6 space-y-3">
          {providers.map((provider) => (
            <div key={provider.provider} className="rounded border p-3">
              <p className="font-medium capitalize">{provider.provider}</p>
              <p className="text-sm text-zinc-500">
                Status: {provider.connected ? "Connected" : "Not connected"} | Mode: {provider.mode}
              </p>
              <p className="mt-1 text-sm text-zinc-500">{provider.details}</p>
            </div>
          ))}
        </div>

        <button
          className="mt-8 rounded border px-4 py-2 text-sm"
          type="button"
          onClick={() => router.push("/dashboard")}
        >
          Back to Dashboard
        </button>
      </main>
    </div>
  );
}
