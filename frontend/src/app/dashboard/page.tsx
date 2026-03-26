"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  discoverFakeJobs,
  getApplications,
  getCurrentUser,
  getJobMatches,
  type JobApplication,
  type JobMatch,
  type UserMe,
} from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserMe | null>(null);
  const [matches, setMatches] = useState<JobMatch[]>([]);
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.replace("/");
      return;
    }
    getCurrentUser(token)
      .then((me) => setUser(me))
      .then(() => Promise.all([getJobMatches(token), getApplications(token)]))
      .then(([m, a]) => {
        setMatches(m);
        setApplications(a);
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        setError("Session expired. Please login again.");
        router.replace("/");
      });
  }, [router]);

  async function discoverJobs() {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    await discoverFakeJobs(token);
    const [m, a] = await Promise.all([getJobMatches(token), getApplications(token)]);
    setMatches(m);
    setApplications(a);
  }

  function logout() {
    localStorage.removeItem("access_token");
    router.replace("/");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
      <main className="w-full max-w-3xl rounded-xl bg-white p-8 shadow dark:bg-zinc-900">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
          Dashboard
        </h1>
        {error ? <p className="mt-4 text-red-500">{error}</p> : null}
        {user ? (
          <div className="mt-4 space-y-2 text-sm text-zinc-700 dark:text-zinc-300">
            <p>
              <strong>ID:</strong> {user.id}
            </p>
            <p>
              <strong>Email:</strong> {user.email}
            </p>
            <p>
              <strong>Name:</strong> {user.full_name ?? "N/A"}
            </p>
          </div>
        ) : (
          <p className="mt-4 text-sm text-zinc-500">Loading profile...</p>
        )}

        <div className="mt-6 rounded border p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium">Job Matches</h2>
            <button className="rounded border px-3 py-1 text-sm" onClick={discoverJobs} type="button">
              Discover Fake Jobs
            </button>
          </div>
          {matches.length ? (
            <ul className="mt-3 space-y-2 text-sm">
              {matches.map((m) => (
                <li key={m.id} className="rounded border p-2">
                  <p className="font-medium">
                    {m.title} - {m.company}
                  </p>
                  <p className="text-zinc-500">
                    {m.location ?? "N/A"} | score: {m.score ?? "N/A"} | source: {m.source}
                  </p>
                  <p className="text-zinc-500">{m.explanation ?? "No explanation yet."}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-sm text-zinc-500">No matches yet. Click discover.</p>
          )}
        </div>

        <div className="mt-4 rounded border p-4">
          <h2 className="text-lg font-medium">Applications</h2>
          {applications.length ? (
            <ul className="mt-3 space-y-2 text-sm">
              {applications.map((a) => (
                <li key={a.id} className="rounded border p-2">
                  Job #{a.job_id} - {a.status} ({a.provider})
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-sm text-zinc-500">No applications yet.</p>
          )}
        </div>

        <button
          className="mt-6 rounded bg-zinc-900 px-4 py-2 text-sm text-white dark:bg-zinc-100 dark:text-zinc-900"
          onClick={logout}
          type="button"
        >
          Logout
        </button>
        <button
          className="mt-6 ml-2 rounded border px-4 py-2 text-sm"
          onClick={() => router.push("/settings/preferences")}
          type="button"
        >
          Preferences
        </button>
        <button
          className="mt-6 ml-2 rounded border px-4 py-2 text-sm"
          onClick={() => router.push("/settings/connections")}
          type="button"
        >
          Connections
        </button>
      </main>
    </div>
  );
}

