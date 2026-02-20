import { useCallback, useRef, useState } from "react";

type Status = "idle" | "loading" | "success" | "error";

/**
 * Lightweight hook wrapping an async API call with loading/error state.
 *
 * Usage:
 *   const { data, error, status, execute } = useApi(listExperiments);
 *   // call execute() to trigger the fetch.
 */
export function useApi<TArgs extends unknown[], TData>(
  fn: (...args: TArgs) => Promise<TData>,
) {
  const [data, setData] = useState<TData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const counter = useRef(0);

  const execute = useCallback(
    async (...args: TArgs) => {
      const id = ++counter.current;
      setStatus("loading");
      setError(null);
      try {
        const result = await fn(...args);
        if (id === counter.current) {
          setData(result);
          setStatus("success");
        }
        return result;
      } catch (err) {
        if (id === counter.current) {
          const msg = err instanceof Error ? err.message : String(err);
          setError(msg);
          setStatus("error");
        }
        return null;
      }
    },
    [fn],
  );

  return { data, error, status, loading: status === "loading", execute };
}
