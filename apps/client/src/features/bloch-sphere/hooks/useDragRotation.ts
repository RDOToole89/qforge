import { useState, useRef, useCallback } from "react";

export interface UseDragRotationReturn {
  rotation: number;
  isDragging: boolean;
  onPD: (e: React.PointerEvent) => void;
  onPM: (e: React.PointerEvent) => void;
  onPU: () => void;
}

export function useDragRotation(): UseDragRotationReturn {
  const [rotation, setRotation] = useState(0.6);
  const [isDragging, setIsDragging] = useState(false);
  const lastXRef = useRef(0);

  const onPD = useCallback((e: React.PointerEvent) => {
    setIsDragging(true);
    lastXRef.current = e.clientX;
  }, []);

  const onPM = useCallback((e: React.PointerEvent) => {
    if (!isDragging) return;
    setRotation((r) => r + (e.clientX - lastXRef.current) * 0.008);
    lastXRef.current = e.clientX;
  }, [isDragging]);

  const onPU = useCallback(() => setIsDragging(false), []);

  return { rotation, isDragging, onPD, onPM, onPU };
}
