export function getBackendUrl(): string {
  return process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";
}

export async function fetchHealth(): Promise<{ status: string }> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/health`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Health check failed with status ${res.status}`);
  }
  return res.json();
}

