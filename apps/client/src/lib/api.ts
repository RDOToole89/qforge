/**
 * Typed API client for the Quantum Experiment Framework backend.
 *
 * All functions throw on non-2xx responses.
 */

import type {
  ExperimentConfig,
  ExperimentResult,
  RegistryEntry,
  StoredResultEntry,
} from "./types";

const DEV_URL = "http://localhost:8000/api";

// For physical devices on the same LAN, change to your machine's IP:
// const DEV_URL = "http://192.168.x.x:8000/api";

const BASE_URL = __DEV__ ? DEV_URL : DEV_URL; // TODO: set prod URL when deployed

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

// ── Registry ──────────────────────────────────────────────────────────

export function listExperiments(): Promise<RegistryEntry[]> {
  return request("/experiments");
}

export function getDefaultConfig(
  name: string,
): Promise<Record<string, unknown>> {
  return request(`/experiments/${encodeURIComponent(name)}/config`);
}

export function getConfigSchema(): Promise<Record<string, unknown>> {
  return request("/experiments/config-schema");
}

// ── Execution ─────────────────────────────────────────────────────────

export function runExperiment(
  config: ExperimentConfig,
): Promise<ExperimentResult> {
  return request("/experiments/run", {
    method: "POST",
    body: JSON.stringify(config),
  });
}

// ── Stored results ────────────────────────────────────────────────────

export function listResults(
  limit = 50,
  offset = 0,
): Promise<StoredResultEntry[]> {
  return request(`/results?limit=${limit}&offset=${offset}`);
}

export function getResult(filename: string): Promise<Record<string, unknown>> {
  return request(`/results/${encodeURIComponent(filename)}`);
}
