import type { CaseRecord, ProviderStatus } from "../types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(detail.detail || "Request failed");
  }
  return response.json() as Promise<T>;
}

export const api = {
  listCases: () => request<CaseRecord[]>("/api/v1/cases"),
  getCase: (id: string) => request<CaseRecord>(`/api/v1/cases/${id}`),
  getProvider: () => request<ProviderStatus>("/api/v1/provider"),
  createDemo: () => request<CaseRecord>("/api/v1/demo", { method: "POST" }),
  createProcurementDemo: () =>
    request<CaseRecord>("/api/v1/demo/procurement", { method: "POST" }),
  createCase: (name: string, files: File[]) => {
    const body = new FormData();
    body.append("name", name);
    body.append("process", "true");
    files.forEach((file) => body.append("files", file));
    return request<CaseRecord>("/api/v1/cases", { method: "POST", body });
  },
  runRecipe: (name: string, recipe: File, files: File[]) => {
    const body = new FormData();
    if (name) body.append("name", name);
    body.append("recipe", recipe);
    files.forEach((file) => body.append("files", file));
    return request<CaseRecord>("/api/v1/recipes/run", { method: "POST", body });
  },
  updateField: (caseId: string, key: string, value: string | number | null) =>
    request<CaseRecord>(`/api/v1/cases/${caseId}/fields/${key}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ value, reviewed: true }),
    }),
  review: (caseId: string, decision: "approved" | "rejected") =>
    request<CaseRecord>(`/api/v1/cases/${caseId}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision, note: "Reviewed in DocuRule workspace" }),
    }),
};
