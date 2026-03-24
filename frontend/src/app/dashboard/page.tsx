"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser, type UserMe } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserMe | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.replace("/");
      return;
    }
    getCurrentUser(token)
      .then((me) => setUser(me))
      .catch(() => {
        localStorage.removeItem("access_token");
        setError("Session expired. Please login again.");
        router.replace("/");
      });
  }, [router]);

  function logout() {
    localStorage.removeItem("access_token");
    router.replace("/");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
      <main className="w-full max-w-xl rounded-xl bg-white p-8 shadow dark:bg-zinc-900">
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

        <button
          className="mt-6 rounded bg-zinc-900 px-4 py-2 text-sm text-white dark:bg-zinc-100 dark:text-zinc-900"
          onClick={logout}
          type="button"
        >
          Logout
        </button>
      </main>
    </div>
  );
}

