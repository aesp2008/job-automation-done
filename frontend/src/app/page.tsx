import { Suspense } from "react";
import { fetchHealth, getBackendUrl } from "@/lib/api";

async function HealthStatus() {
  let status: string;
  let errorText: string | null = null;
  try {
    const data = await fetchHealth();
    status = data.status;
  } catch (error) {
    status = "unreachable";
    errorText = error instanceof Error ? error.message : String(error);
  }

  return (
    <div className="mt-4 text-sm text-zinc-600 dark:text-zinc-400">
      <p>
        Backend URL: <span className="font-mono">{getBackendUrl()}</span>
      </p>
      <p>
        Backend health:{" "}
        <span
          className={
            status === "ok" ? "text-emerald-600 font-semibold" : "text-red-500"
          }
        >
          {status}
        </span>
      </p>
      {errorText ? (
        <p className="mt-1 font-mono text-xs text-red-500">{errorText}</p>
      ) : null}
    </div>
  );
}

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-center py-32 px-16 bg-white dark:bg-black text-center">
        <h1 className="text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
          Job Automation Dashboard (MVP)
        </h1>
        <p className="mt-2 max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
          We&apos;re just getting started. For now, this page checks whether
          the backend is up and responding.
        </p>
        <Suspense fallback={<p className="mt-4 text-sm">Checking health…</p>}>
          {/* @ts-expect-error Async Server Component */}
          <HealthStatus />
        </Suspense>
      </main>
    </div>
  );
}
