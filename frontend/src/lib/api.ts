export type RegisterPayload = {
  email: string;
  password: string;
  full_name?: string;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type AuthTokenResponse = {
  access_token: string;
  token_type: string;
};

export type UserMe = {
  id: number;
  email: string;
  full_name: string | null;
};

export function getBackendUrl(): string {
  return process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";
}

async function parseJsonOrThrow<T>(res: Response): Promise<T> {
  const text = await res.text();
  const data = text ? JSON.parse(text) : {};
  if (!res.ok) {
    const detail = (data as { detail?: string }).detail ?? `Request failed (${res.status})`;
    throw new Error(detail);
  }
  return data as T;
}

export async function fetchHealth(): Promise<{ status: string }> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/health`, { cache: "no-store" });
  return parseJsonOrThrow<{ status: string }>(res);
}

export async function registerUser(payload: RegisterPayload): Promise<UserMe> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/users/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonOrThrow<UserMe>(res);
}

export async function loginUser(payload: LoginPayload): Promise<AuthTokenResponse> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return parseJsonOrThrow<AuthTokenResponse>(res);
}

export async function getCurrentUser(token: string): Promise<UserMe> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return parseJsonOrThrow<UserMe>(res);
}

