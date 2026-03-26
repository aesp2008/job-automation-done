"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getProviderStatuses, type ProviderStatus } from "@/lib/api";

export default function ConnectionsPage() {
  const router = useRouter();
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.replace("/");
      return;
    }
    getProviderStatuses(token)
      .then((data) => setProviders(data))
      .catch(() => {
        setError("Unable to load provider statuses.");
      });
  }, [router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
      <main className="w-full max-w-2xl rounded-xl bg-white p-8 shadow dark:bg-zinc-900">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
          Provider Connections
        </h1>
        <p className="mt-1 text-sm text-zinc-500">
          This is a status-only MVP view. Real credential setup comes later.
        </p>

        {error ? <p className="mt-4 text-sm text-red-500">{error}</p> : null}

        <div className="mt-5 space-y-3">
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

