import type { Assessment, CaseInput, CreditCase } from "./types";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8080";

export type Credentials = { username: string; password: string };

async function request<T>(path: string, credentials: Credentials, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, {
    ...init,
    headers: {
      Authorization: `Basic ${btoa(`${credentials.username}:${credentials.password}`)}`,
      "Content-Type": "application/json",
      ...init.headers,
    },
  });
  if (!response.ok) {
    const message = response.status === 401 ? "Login failed" : `Request failed (${response.status})`;
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export function createCase(input: CaseInput, credentials: Credentials): Promise<CreditCase> {
  return request("/api/v1/cases", credentials, { method: "POST", body: JSON.stringify(input) });
}

export function assessCase(caseId: string, credentials: Credentials): Promise<Assessment> {
  return request(`/api/v1/cases/${caseId}/assessments`, credentials, { method: "POST" });
}

export function decideCase(
  caseId: string,
  decision: string,
  comment: string,
  credentials: Credentials,
): Promise<unknown> {
  return request(`/api/v1/cases/${caseId}/decisions`, credentials, {
    method: "POST",
    body: JSON.stringify({ decision, comment }),
  });
}

