/**
 * Hook that fetches the real hardware backend list and validates a proposed
 * config against a backend before submission.
 *
 * Both backend endpoints degrade gracefully (HTTP 200 with `available: false`)
 * when IBM credentials are absent, so this hook never throws into the UI; it
 * surfaces the backend-provided `reason` instead. The backend list here is the
 * single source of truth for the hardware backend picker — there is no
 * hardcoded fallback list.
 */

import { useEffect, useMemo, useState } from "react";
import {
  getHardwareBackends,
  validateHardwareConfig,
  type HardwareBackend,
  type HardwareValidationResponse,
} from "@/src/lib/api";
import type { ExperimentConfig } from "../../lib/types";

const VALIDATE_DEBOUNCE_MS = 400;

export interface UseHardwareValidationReturn {
  /** Live backends from the backend (empty when unavailable). */
  backends: HardwareBackend[];
  /** Whether the live backend list is available (credentials present). */
  backendsAvailable: boolean;
  /** Backend-provided reason the list is unavailable, if any. */
  backendsReason: string | null;
  backendsLoading: boolean;
  /** Latest feasibility result, or null when not yet validated / not hardware. */
  validation: HardwareValidationResponse | null;
  validating: boolean;
}

export function useHardwareValidation(
  enabled: boolean,
  buildConfig: () => ExperimentConfig,
): UseHardwareValidationReturn {
  const [backends, setBackends] = useState<HardwareBackend[]>([]);
  const [backendsAvailable, setBackendsAvailable] = useState(false);
  const [backendsReason, setBackendsReason] = useState<string | null>(null);
  const [backendsLoading, setBackendsLoading] = useState(false);
  const [validation, setValidation] = useState<HardwareValidationResponse | null>(null);
  const [validating, setValidating] = useState(false);

  // ── Fetch backend list when hardware mode becomes active ──────────────
  useEffect(() => {
    if (!enabled) {
      setBackends([]);
      setBackendsAvailable(false);
      setBackendsReason(null);
      return;
    }
    let cancelled = false;
    setBackendsLoading(true);
    getHardwareBackends()
      .then((res) => {
        if (cancelled) return;
        setBackends(res.backends ?? []);
        setBackendsAvailable(res.available);
        setBackendsReason(res.reason ?? null);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setBackends([]);
        setBackendsAvailable(false);
        setBackendsReason(err instanceof Error ? err.message : String(err));
      })
      .finally(() => {
        if (!cancelled) setBackendsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [enabled]);

  // Serialize the config so the validation effect re-runs only on real changes.
  const configKey = useMemo(
    () => (enabled ? JSON.stringify(buildConfig()) : ""),
    [enabled, buildConfig],
  );

  // ── Validate the config against a real backend (debounced) ────────────
  useEffect(() => {
    if (!enabled || !configKey) {
      setValidation(null);
      return;
    }
    let cancelled = false;
    setValidating(true);
    const handle = setTimeout(() => {
      validateHardwareConfig(JSON.parse(configKey) as ExperimentConfig)
        .then((res) => {
          if (!cancelled) setValidation(res);
        })
        .catch((err: unknown) => {
          if (!cancelled) {
            setValidation({
              available: false,
              reason: err instanceof Error ? err.message : String(err),
            });
          }
        })
        .finally(() => {
          if (!cancelled) setValidating(false);
        });
    }, VALIDATE_DEBOUNCE_MS);
    return () => {
      cancelled = true;
      clearTimeout(handle);
    };
  }, [enabled, configKey]);

  return {
    backends,
    backendsAvailable,
    backendsReason,
    backendsLoading,
    validation,
    validating,
  };
}
