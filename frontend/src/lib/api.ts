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

export type UserPreferences = {
  target_roles: string[];
  locations: string[];
  salary_min: number | null;
  salary_max: number | null;
  job_types: string[];
  aggressiveness: number;
};

export type JobMatch = {
  id: number;
  title: string;
  company: string;
  location: string | null;
  score: number | null;
  explanation: string | null;
  source: string;
};

export type JobApplication = {
  id: number;
  job_id: number;
  status: string;
  provider: string;
};

export type ProviderStatus = {
  provider: string;
  connected: boolean;
  mode: string;
  details: string;
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

export async function getMyPreferences(token: string): Promise<UserPreferences> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/users/me/preferences`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return parseJsonOrThrow<UserPreferences>(res);
}

export async function updateMyPreferences(
  token: string,
  payload: UserPreferences
): Promise<UserPreferences> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/users/me/preferences`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  return parseJsonOrThrow<UserPreferences>(res);
}

export async function uploadResume(
  token: string,
  file: File
): Promise<{
  message: string;
  resume_path: string;
  parsed_summary?: {
    filename: string;
    file_size_kb: number;
    extension: string;
    skills_detected: string[];
    summary: string;
  };
}> {
  const backendUrl = getBackendUrl();
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${backendUrl}/users/me/resume`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  return parseJsonOrThrow<{
    message: string;
    resume_path: string;
    parsed_summary?: {
      filename: string;
      file_size_kb: number;
      extension: string;
      skills_detected: string[];
      summary: string;
    };
  }>(res);
}

export async function discoverFakeJobs(token: string): Promise<{ created_jobs: number; total_fake_jobs: number }> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/jobs/discover/fake`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  return parseJsonOrThrow<{ created_jobs: number; total_fake_jobs: number }>(res);
}

export async function getJobMatches(token: string): Promise<JobMatch[]> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/jobs/matches`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return parseJsonOrThrow<JobMatch[]>(res);
}

export async function getApplications(token: string): Promise<JobApplication[]> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/jobs/applications`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return parseJsonOrThrow<JobApplication[]>(res);
}

export async function getProviderStatuses(token: string): Promise<ProviderStatus[]> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/integrations/status`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return parseJsonOrThrow<ProviderStatus[]>(res);
}

