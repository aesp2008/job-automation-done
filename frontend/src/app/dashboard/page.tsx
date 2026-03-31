"use client";

import { startTransition, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  discoverFakeJobs,
  discoverProviderJobs,
  downloadTailoredResumeFile,
  getApplications,
  getCurrentUser,
  getJobMatches,
  getJobTailoring,
  markManualApplicationComplete,
  runAutoApply,
  type JobApplication,
  type JobMatch,
  type JobTailoring,
  type UserMe,
} from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserMe | null>(null);
  const [matches, setMatches] = useState<JobMatch[]>([]);
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");
  const [tailoringByJobId, setTailoringByJobId] = useState<Record<number, JobTailoring | null>>({});

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.replace("/");
      return;
    }
    getCurrentUser(token)
      .then((me) => {
        startTransition(() => setUser(me));
        return Promise.all([getJobMatches(token), getApplications(token)]);
      })
      .then(([m, a]) => {
        startTransition(() => {
          setMatches(m);
          setApplications(a);
        });
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        setError("Session expired. Please login again.");
        router.replace("/");
      });
  }, [router]);

  async function refreshLists() {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    const [m, a] = await Promise.all([getJobMatches(token), getApplications(token)]);
    setMatches(m);
    setApplications(a);
  }

  async function discoverJobs() {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setBusy("Discovering demo jobs…");
    await discoverFakeJobs(token);
    await refreshLists();
    setBusy("");
  }

  async function discoverAllBoards() {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setBusy("Pulling jobs from all configured boards…");
    await discoverProviderJobs(token);
    await refreshLists();
    setBusy("");
  }

  async function tryAutoApply() {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setBusy("Running automated apply (where supported)…");
    const result = await runAutoApply(token);
    await refreshLists();
    setBusy(
      `Auto-apply finished: ${result.auto_applied} automated, ${result.manual_required} need manual posting, ${result.skipped_low_score} skipped (score below threshold).`
    );
    setTimeout(() => setBusy(""), 8000);
  }

  async function loadTailoring(jobId: number) {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setBusy("Building JD-tailored resume draft…");
    try {
      const t = await getJobTailoring(token, jobId);
      setTailoringByJobId((prev) => ({ ...prev, [jobId]: t }));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Tailoring failed");
    }
    setBusy("");
  }

  async function saveTailoredFile(jobId: number) {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    setBusy("Downloading .txt draft…");
    try {
      const blob = await downloadTailoredResumeFile(token, jobId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `tailored-resume-${jobId}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Download failed");
    }
    setBusy("");
  }

  async function confirmManualDone(app: JobApplication) {
    const token = localStorage.getItem("access_token");
    if (!token) return;
    await markManualApplicationComplete(token, app.id);
    await refreshLists();
  }

  function logout() {
    localStorage.removeItem("access_token");
    router.replace("/");
  }

  return (
    <div className="flex min-h-screen items-start justify-center bg-zinc-50 py-10 dark:bg-black">
      <main className="w-full max-w-3xl rounded-xl bg-white p-8 shadow dark:bg-zinc-900">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
          Dashboard
        </h1>
        {error ? <p className="mt-4 text-red-500">{error}</p> : null}
        {busy ? <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">{busy}</p> : null}
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
          <p className="mt-4 text-sm text-zinc-500">Loading profile…</p>
        )}

        <div className="mt-6 rounded border p-4">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-medium">Job Matches</h2>
            <button
              className="rounded border px-3 py-1 text-sm"
              onClick={discoverJobs}
              type="button"
            >
              Discover demo jobs
            </button>
            <button
              className="rounded border px-3 py-1 text-sm"
              onClick={discoverAllBoards}
              type="button"
            >
              Discover all boards
            </button>
            <button
              className="rounded border border-amber-200 bg-amber-50 px-3 py-1 text-sm dark:border-amber-800 dark:bg-amber-950"
              onClick={tryAutoApply}
              type="button"
            >
              Run auto-apply
            </button>
          </div>
          <p className="mt-2 text-xs text-zinc-500">
            Auto-apply only runs where a connector supports it. Failures and unsupported boards move to{" "}
            <strong>manual required</strong> with the posting link.
          </p>
          {matches.length ? (
            <ul className="mt-3 space-y-3 text-sm">
              {matches.map((m) => (
                <li key={m.id} className="rounded border p-2">
                  <p className="font-medium">
                    {m.title} — {m.company}
                  </p>
                  <p className="text-zinc-500">
                    {m.location ?? "N/A"} | score: {m.score ?? "N/A"} | source: {m.source}
                  </p>
                  <p className="text-zinc-500">{m.explanation ?? "No explanation yet."}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <button
                      type="button"
                      className="rounded border px-2 py-1 text-xs"
                      onClick={() => loadTailoring(m.id)}
                    >
                      Tailor resume to JD
                    </button>
                    <button
                      type="button"
                      className="rounded border px-2 py-1 text-xs"
                      onClick={() => saveTailoredFile(m.id)}
                    >
                      Download tailored .txt
                    </button>
                  </div>
                  {tailoringByJobId[m.id] ? (
                    <div className="mt-3 rounded bg-zinc-100 p-2 text-xs dark:bg-zinc-800">
                      <p className="font-medium text-zinc-800 dark:text-zinc-200">
                        {tailoringByJobId[m.id]!.professional_summary}
                      </p>
                      <p className="mt-1 text-zinc-600 dark:text-zinc-400">
                        <strong>JD skills:</strong>{" "}
                        {tailoringByJobId[m.id]!.jd_skills_highlighted.join(", ") || "—"}
                      </p>
                      <p className="text-zinc-600 dark:text-zinc-400">
                        <strong>Matched your resume:</strong>{" "}
                        {tailoringByJobId[m.id]!.skills_matched_with_jd.join(", ") || "—"}
                      </p>
                      <ul className="mt-1 list-inside list-disc text-zinc-600 dark:text-zinc-400">
                        {tailoringByJobId[m.id]!.suggested_bullets.map((b, i) => (
                          <li key={`${m.id}-b-${i}`}>{b}</li>
                        ))}
                      </ul>
                    </div>
                  ) : null}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-sm text-zinc-500">No matches yet. Run discovery.</p>
          )}
        </div>

        <div className="mt-4 rounded border p-4">
          <h2 className="text-lg font-medium">Applications</h2>
          {applications.length ? (
            <ul className="mt-3 space-y-3 text-sm">
              {applications.map((a) => (
                <li key={a.id} className="rounded border p-2">
                  <p className="font-medium">
                    {a.job_title ?? `Job #${a.job_id}`}
                    {a.company ? ` — ${a.company}` : ""}
                  </p>
                  <p className="text-zinc-500">
                    Status: <strong>{a.status}</strong> · {a.provider}
                  </p>
                  {a.status_detail ? (
                    <p className="text-xs text-zinc-600 dark:text-zinc-400">{a.status_detail}</p>
                  ) : null}
                  <div className="mt-2 flex flex-wrap gap-2">
                    {a.job_url ? (
                      <a
                        className="rounded border border-blue-200 bg-blue-50 px-2 py-1 text-xs text-blue-900 dark:border-blue-800 dark:bg-blue-950 dark:text-blue-100"
                        href={a.job_url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open posting
                      </a>
                    ) : null}
                    {a.status === "manual_required" || a.status === "queued" ? (
                      <button
                        type="button"
                        className="rounded border px-2 py-1 text-xs"
                        onClick={() => confirmManualDone(a)}
                      >
                        Mark applied manually
                      </button>
                    ) : null}
                    <button
                      type="button"
                      className="rounded border px-2 py-1 text-xs"
                      onClick={() => loadTailoring(a.job_id)}
                    >
                      Tailor resume
                    </button>
                  </div>
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
