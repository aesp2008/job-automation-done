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
  status_detail?: string | null;
  job_title?: string | null;
  company?: string | null;
  job_url?: string | null;
};

export type JobTailoring = {
  job_title: string;
  company: string;
  jd_skills_highlighted: string[];
  resume_skills_detected: string[];
  skills_matched_with_jd: string[];
  skills_gaps_vs_jd: string[];
  skills_section_ordered: string[];
  suggested_bullets: string[];
  professional_summary: string;
  full_text_draft: string;
  resume_excerpt?: string;
  resume_extraction_note?: string | null;
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
    emails_found?: string[];
    text_preview?: string;
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
      emails_found?: string[];
      text_preview?: string;
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

export async function discoverProviderJobs(
  token: string
): Promise<{ created_jobs: number; providers_touched: number }> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/jobs/discover/providers`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  return parseJsonOrThrow<{ created_jobs: number; providers_touched: number }>(res);
}

export async function runAutoApply(token: string): Promise<{
  auto_applied: number;
  manual_required: number;
  skipped_low_score: number;
  message?: string;
}> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/jobs/applications/auto-apply/run`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  return parseJsonOrThrow<{
    auto_applied: number;
    manual_required: number;
    skipped_low_score: number;
    message?: string;
  }>(res);
}

export async function markManualApplicationComplete(
  token: string,
  applicationId: number
): Promise<{ id: number; status: string }> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/jobs/applications/${applicationId}/manual-complete`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  return parseJsonOrThrow<{ id: number; status: string }>(res);
}

export async function getJobTailoring(token: string, jobId: number): Promise<JobTailoring> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/jobs/${jobId}/tailoring`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return parseJsonOrThrow<JobTailoring>(res);
}

export async function downloadTailoredResumeFile(token: string, jobId: number): Promise<Blob> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/jobs/${jobId}/tailored-resume.txt`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const text = await res.text();
    let detail = `Request failed (${res.status})`;
    try {
      const j = JSON.parse(text) as { detail?: string };
      if (j.detail) detail = j.detail;
    } catch {
      /* use default */
    }
    throw new Error(detail);
  }
  return res.blob();
}

export async function downloadTailoredResumeDocx(token: string, jobId: number): Promise<Blob> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/jobs/${jobId}/tailored-resume.docx`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const text = await res.text();
    let detail = `Request failed (${res.status})`;
    try {
      const j = JSON.parse(text) as { detail?: string };
      if (j.detail) detail = j.detail;
    } catch {
      /* use default */
    }
    throw new Error(detail);
  }
  return res.blob();
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

export type IntegrationConnection = {
  provider: string;
  config: Record<string, unknown>;
};

export async function getIntegrationConnections(token: string): Promise<IntegrationConnection[]> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/integrations/connections`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  return parseJsonOrThrow<IntegrationConnection[]>(res);
}

export async function putRssFeedConnection(token: string, rssUrl: string): Promise<{ provider: string; rss_url: string }> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/integrations/connections/rss_feed`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ rss_url: rssUrl }),
  });
  return parseJsonOrThrow<{ provider: string; rss_url: string }>(res);
}

export async function deleteRssFeedConnection(token: string): Promise<{ ok: boolean }> {
  const backendUrl = getBackendUrl();
  const res = await fetch(`${backendUrl}/integrations/connections/rss_feed`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  return parseJsonOrThrow<{ ok: boolean }>(res);
}

