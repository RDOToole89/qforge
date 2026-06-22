/**
 * Tests for the hardware API helpers. The backend endpoints degrade to
 * `available: false` (HTTP 200) when IBM credentials are absent, so these
 * helpers must surface that shape rather than throwing.
 */
import { afterEach, describe, expect, it, vi } from "vitest";
import { getHardwareBackends, validateHardwareConfig } from "../api";
import type { ExperimentConfig } from "../types";

function mockFetch(body: unknown, ok = true, status = 200) {
  return vi.fn().mockResolvedValue({
    ok,
    status,
    json: () => Promise.resolve(body),
    text: () =>
      Promise.resolve(typeof body === "string" ? body : JSON.stringify(body)),
  });
}

describe("hardware api helpers", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("getHardwareBackends parses an available backend list", async () => {
    const payload = {
      available: true,
      backends: [
        {
          name: "ibm_test",
          num_qubits: 127,
          max_shots: 100000,
          basis_gates: ["sx", "x", "cz"],
          operational: true,
          simulator: false,
        },
      ],
    };
    const f = mockFetch(payload);
    vi.stubGlobal("fetch", f);

    const res = await getHardwareBackends();

    expect(res.available).toBe(true);
    expect(res.backends).toHaveLength(1);
    expect(res.backends[0].name).toBe("ibm_test");
    expect(f).toHaveBeenCalledWith(
      expect.stringContaining("/hardware/backends"),
      expect.any(Object),
    );
  });

  it("getHardwareBackends surfaces the unavailable reason", async () => {
    const payload = { available: false, reason: "no credentials", backends: [] };
    vi.stubGlobal("fetch", mockFetch(payload));

    const res = await getHardwareBackends();

    expect(res.available).toBe(false);
    expect(res.reason).toBe("no credentials");
    expect(res.backends).toEqual([]);
  });

  it("validateHardwareConfig POSTs the config and parses infeasibility", async () => {
    const payload = {
      available: true,
      feasible: false,
      violations: ["Circuit needs 5 qubits but backend has 2."],
      warnings: ["Only 50 shots requested."],
      backend_name: "ibm_test",
      capabilities: {},
    };
    const f = mockFetch(payload);
    vi.stubGlobal("fetch", f);

    const config = {
      num_qubits: 5,
      state_type: "GHZ",
      shots: 50,
      noise_enabled: false,
      sim_mode: "hardware",
    } as ExperimentConfig;

    const res = await validateHardwareConfig(config);

    expect(res.available).toBe(true);
    expect(res.feasible).toBe(false);
    expect(res.violations).toContain("Circuit needs 5 qubits but backend has 2.");
    expect(res.warnings).toHaveLength(1);

    const [url, init] = f.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("/hardware/validate");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body as string)).toMatchObject({ num_qubits: 5 });
  });

  it("throws on a non-2xx response", async () => {
    vi.stubGlobal("fetch", mockFetch("boom", false, 500));
    await expect(getHardwareBackends()).rejects.toThrow("API 500");
  });
});
