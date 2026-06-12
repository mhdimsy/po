export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  return parseResponse<T>(response);
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined
  });
  return parseResponse<T>(response);
}

export async function apiPut<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'PUT',
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined
  });
  return parseResponse<T>(response);
}

export async function apiUpload<T>(path: string, files: File[], extra?: Record<string, string>): Promise<T> {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  for (const [key, value] of Object.entries(extra ?? {})) {
    formData.append(key, value);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    body: formData
  });
  return parseResponse<T>(response);
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}
