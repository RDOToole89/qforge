/**
 * Typed API client for the QForge backend.
 *
 * All functions throw on non-2xx responses.
 */

import type {
  BlochSweepRequest,
  BlochSweepResponse,
  BlochVisualizerData,
  ExperimentConfig,
  ExperimentResult,
  RegistryEntry,
  StoredResultEntry,
} from "./types";

const DEV_URL = "http://localhost:8000/api";

// For physical devices on the same LAN, change to your machine's IP:
// const DEV_URL = "http://192.168.x.x:8000/api";

const PROD_URL = process.env.EXPO_PUBLIC_API_URL ?? "";
const BASE_URL = __DEV__ ? DEV_URL : PROD_URL;

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

export function previewCircuit(
  config: ExperimentConfig,
): Promise<{ circuit: unknown; diagram: string; stats: { depth: number; num_gates: number; num_qubits: number } }> {
  return request("/experiments/preview", {
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

export function getBlochData(filename: string): Promise<BlochVisualizerData> {
  // filename contains path separators (e.g. "2026-03-07/GHZ_.../analysis.json")
  // which must be passed as literal slashes for FastAPI's {filename:path} parameter
  return request(`/bloch/${filename}`);
}

export function runBlochSweep(req: BlochSweepRequest): Promise<BlochSweepResponse> {
  return request("/bloch/sweep", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

// ── Hardware (real IBM Quantum backends) ──────────────────────────────

/** Capabilities of a single hardware backend (see apps/api/routes/hardware.py). */
export interface HardwareBackend {
  name: string | null;
  num_qubits: number | null;
  max_shots: number | null;
  basis_gates: string[];
  operational: boolean;
  simulator: boolean;
}

/** Response of `GET /api/hardware/backends`. */
export interface HardwareBackendsResponse {
  available: boolean;
  backends: HardwareBackend[];
  /** Why no backends are available (only present when `available` is false). */
  reason?: string;
}

/** Response of `POST /api/hardware/validate`. */
export interface HardwareValidationResponse {
  available: boolean;
  /** Present only when `available` is true. */
  feasible?: boolean;
  violations?: string[];
  warnings?: string[];
  backend_name?: string | null;
  capabilities?: HardwareBackend;
  /** Why validation could not run (only present when `available` is false). */
  reason?: string;
}

/**
 * List operational, non-simulator IBM Quantum backends with capabilities.
 *
 * Returns `{ available: false, reason, backends: [] }` (HTTP 200) when IBM
 * credentials are absent or the service is unreachable.
 */
export function getHardwareBackends(): Promise<HardwareBackendsResponse> {
  return request("/hardware/backends");
}

/**
 * Validate an experiment config against a real backend before submission.
 *
 * Returns `{ available: false, reason }` (HTTP 200) when credentials/service
 * are missing; otherwise reports `feasible`, `violations`, and `warnings`.
 */
export function validateHardwareConfig(
  config: ExperimentConfig,
): Promise<HardwareValidationResponse> {
  return request("/hardware/validate", {
    method: "POST",
    body: JSON.stringify(config),
  });
}
