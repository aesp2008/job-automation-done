"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  getMyPreferences,
  updateMyPreferences,
  uploadResume,
  type UserPreferences,
} from "@/lib/api";

const DEFAULT_PREFS: UserPreferences = {
  target_roles: [],
  locations: [],
  salary_min: null,
  salary_max: null,
  job_types: [],
  aggressiveness: 50,
};

export default function PreferencesPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [prefs, setPrefs] = useState<UserPreferences>(DEFAULT_PREFS);
  const [rolesText, setRolesText] = useState("");
  const [locationsText, setLocationsText] = useState("");
  const [jobTypesText, setJobTypesText] = useState("");
  const [message, setMessage] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  useEffect(() => {
    const t = localStorage.getItem("access_token");
    if (!t) {
      router.replace("/");
      return;
    }
    setToken(t);
    getMyPreferences(t)
      .then((data) => {
        setPrefs(data);
        setRolesText(data.target_roles.join(", "));
        setLocationsText(data.locations.join(", "));
        setJobTypesText(data.job_types.join(", "));
      })
      .catch(() => router.replace("/"));
  }, [router]);

  async function onSave(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!token) return;
    setMessage("");
    const payload: UserPreferences = {
      target_roles: rolesText.split(",").map((x) => x.trim()).filter(Boolean),
      locations: locationsText.split(",").map((x) => x.trim()).filter(Boolean),
      job_types: jobTypesText.split(",").map((x) => x.trim()).filter(Boolean),
      salary_min: prefs.salary_min,
      salary_max: prefs.salary_max,
      aggressiveness: prefs.aggressiveness,
    };
    try {
      const saved = await updateMyPreferences(token, payload);
      setPrefs(saved);
      setMessage("Preferences saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to save preferences");
    }
  }

  async function onUploadResume(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!token || !resumeFile) return;
    setMessage("");
    try {
      const result = await uploadResume(token, resumeFile);
      setMessage(`Resume uploaded: ${result.resume_path}`);
      setResumeFile(null);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to upload resume");
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
      <main className="w-full max-w-xl rounded-xl bg-white p-8 shadow dark:bg-zinc-900">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
          Preferences
        </h1>
        <p className="mt-1 text-sm text-zinc-500">
          Comma-separated values are supported for roles, locations, and job types.
        </p>

        <form className="mt-6 space-y-3" onSubmit={onUploadResume}>
          <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
            Resume
          </h2>
          <input
            className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={(e) => setResumeFile(e.target.files?.[0] ?? null)}
          />
          <button
            className="rounded border px-3 py-2 text-sm"
            type="submit"
            disabled={!resumeFile}
          >
            Upload Resume
          </button>
        </form>

        <form className="mt-6 space-y-3" onSubmit={onSave}>
          <h2 className="pt-2 text-lg font-medium text-zinc-900 dark:text-zinc-100">
            Job Preferences
          </h2>
          <input
            className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
            placeholder="Target roles (e.g. Backend Engineer, SDE)"
            value={rolesText}
            onChange={(e) => setRolesText(e.target.value)}
          />
          <input
            className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
            placeholder="Locations (e.g. Pune, Remote)"
            value={locationsText}
            onChange={(e) => setLocationsText(e.target.value)}
          />
          <input
            className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
            placeholder="Job types (e.g. Full-time, Internship)"
            value={jobTypesText}
            onChange={(e) => setJobTypesText(e.target.value)}
          />
          <div className="grid grid-cols-2 gap-3">
            <input
              className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
              type="number"
              placeholder="Salary min"
              value={prefs.salary_min ?? ""}
              onChange={(e) =>
                setPrefs((p) => ({ ...p, salary_min: e.target.value ? Number(e.target.value) : null }))
              }
            />
            <input
              className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
              type="number"
              placeholder="Salary max"
              value={prefs.salary_max ?? ""}
              onChange={(e) =>
                setPrefs((p) => ({ ...p, salary_max: e.target.value ? Number(e.target.value) : null }))
              }
            />
          </div>
          <label className="block text-sm text-zinc-600 dark:text-zinc-300">
            Aggressiveness: {prefs.aggressiveness}
          </label>
          <input
            className="w-full"
            type="range"
            min={0}
            max={100}
            value={prefs.aggressiveness}
            onChange={(e) => setPrefs((p) => ({ ...p, aggressiveness: Number(e.target.value) }))}
          />

          {message ? <p className="text-sm text-zinc-500">{message}</p> : null}

          <div className="flex gap-2">
            <button
              className="rounded bg-zinc-900 px-4 py-2 text-sm text-white dark:bg-zinc-100 dark:text-zinc-900"
              type="submit"
            >
              Save
            </button>
            <button
              className="rounded border px-4 py-2 text-sm"
              type="button"
              onClick={() => router.push("/dashboard")}
            >
              Back
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}

