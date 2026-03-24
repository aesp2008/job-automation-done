"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  fetchHealth,
  getBackendUrl,
  loginUser,
  registerUser,
} from "@/lib/api";

type Mode = "login" | "register";

export default function Home() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [health, setHealth] = useState("checking");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHealth()
      .then((res) => setHealth(res.status))
      .catch(() => setHealth("unreachable"));
  }, []);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await registerUser({
          email,
          password,
          full_name: fullName || undefined,
        });
      }
      const token = await loginUser({ email, password });
      localStorage.setItem("access_token", token.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="w-full max-w-md rounded-xl bg-white p-8 shadow dark:bg-zinc-900">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
          Job Automation MVP
        </h1>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          Backend URL: <span className="font-mono">{getBackendUrl()}</span>
        </p>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Backend health:{" "}
          <span className={health === "ok" ? "text-emerald-600" : "text-red-500"}>
            {health}
          </span>
        </p>

        <div className="mt-6 flex gap-2">
          <button
            className={`rounded px-3 py-1 text-sm ${mode === "login" ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900" : "bg-zinc-200 dark:bg-zinc-700"}`}
            onClick={() => setMode("login")}
            type="button"
          >
            Login
          </button>
          <button
            className={`rounded px-3 py-1 text-sm ${mode === "register" ? "bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900" : "bg-zinc-200 dark:bg-zinc-700"}`}
            onClick={() => setMode("register")}
            type="button"
          >
            Register
          </button>
        </div>

        <form className="mt-4 space-y-3" onSubmit={onSubmit}>
          {mode === "register" ? (
            <input
              className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
              placeholder="Full name (optional)"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          ) : null}
          <input
            className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
            placeholder="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            className="w-full rounded border px-3 py-2 text-sm dark:bg-zinc-800"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error ? <p className="text-sm text-red-500">{error}</p> : null}
          <button
            className="w-full rounded bg-zinc-900 px-4 py-2 text-sm text-white disabled:opacity-60 dark:bg-zinc-100 dark:text-zinc-900"
            type="submit"
            disabled={loading}
          >
            {loading ? "Please wait..." : mode === "login" ? "Login" : "Register"}
          </button>
        </form>
      </main>
    </div>
  );
}
