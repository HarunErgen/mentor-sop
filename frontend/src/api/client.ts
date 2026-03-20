import type {
  FullUserInput,
  JobCreateResponse,
  JobStatusResponse,
  ListJobsResponse,
} from "../types";

const API_BASE =
  import.meta.env.VITE_API_URL || "";

function getBase(): string {
  return API_BASE.replace(/\/$/, "");
}

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function generateSop(input: FullUserInput): Promise<JobCreateResponse> {
  const res = await fetch(`${getBase()}/api/sop/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeaders() },
    body: JSON.stringify(input),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const res = await fetch(`${getBase()}/api/sop/jobs/${jobId}`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getUserJobs(): Promise<ListJobsResponse> {
  const res = await fetch(`${getBase()}/api/sop/jobs`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export type JobEventSnapshot = {
  job_id: string;
  status: string;
  current_step: string;
  created_at?: string | null;
  result?: import("../types").SOPReport | null;
  error?: string | null;
};

export function subscribeJobEvents(
  jobId: string,
  onEvent: (data: JobEventSnapshot) => void,
  onError?: (err: Event) => void
): () => void {
  const token = localStorage.getItem("token") || "";
  const url = `${getBase()}/api/sop/jobs/${jobId}/events?token=${encodeURIComponent(token)}`;
  const es = new EventSource(url);

  es.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data) as JobEventSnapshot;
      onEvent(data);
      if (data.status === "completed" || data.status === "failed") {
        es.close();
      }
    } catch {
      // ignore non-JSON (e.g. heartbeat comment)
    }
  };

  es.onerror = (err) => {
    onError?.(err);
  };

  return () => es.close();
}
