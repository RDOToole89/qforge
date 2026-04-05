"use dom";

import { useState, useEffect, useCallback, useRef } from "react";
import { colors, fonts } from "../styles";

const STORAGE_KEY = "circuit-builder-onboarding-v2";

/** Actions the onboarding can trigger on the parent */
export interface OnboardingActions {
  loadBellPreset: () => void;
  playBloch: () => void;
  resetBloch: () => void;
  openFullscreen: () => void;
  closeFullscreen: () => void;
}

interface OnboardingStep {
  title: string;
  description: string;
  /** data-onboarding attribute value to highlight */
  highlight: string | null;
  /** Tooltip position relative to the highlighted element */
  tooltipSide: "right" | "bottom" | "left" | "center";
  /** Action to run when entering this step */
  onEnter?: keyof OnboardingActions;
}

const STEPS: OnboardingStep[] = [
  {
    highlight: null,
    tooltipSide: "center",
    title: "Welcome to the Quantum Circuit Builder",
    description: "Build quantum circuits, watch states evolve on the Bloch sphere, and explore entanglement \u2014 all in real time.\n\nWe've loaded a Bell State circuit to show you around. Let's walk through the interface.",
    onEnter: "loadBellPreset",
  },
  {
    highlight: "mode-toggle",
    tooltipSide: "bottom",
    title: "Input Modes",
    description: "Circuit Builder lets you build circuits gate by gate. Direct State lets you load ideal quantum states (Bell, GHZ, W) and instantly analyze their properties without building a circuit.",
  },
  {
    highlight: "toolbar",
    tooltipSide: "bottom",
    title: "Toolbar & Presets",
    description: "The Presets dropdown has 22 well-known circuits \u2014 from Bell states to Grover's search. Each loads with step-by-step explanations and real-world applications. You can also Export your circuit as JSON.",
  },
  {
    highlight: "palette",
    tooltipSide: "bottom",
    title: "Gate Palette",
    description: "Click a gate to select it, then click a qubit wire to place it. Or drag and drop directly. You have Hadamard, Pauli gates, rotations, CNOT, CZ, SWAP, and Toffoli \u2014 enough for any textbook circuit.",
  },
  {
    highlight: "canvas",
    tooltipSide: "bottom",
    title: "Your Circuit",
    description: "Here's the Bell State: H on q0 creates superposition, then CNOT entangles q0 with q1. Click any gate to see its properties or remove it.\n\nBelow the canvas, the State Evolution shows the quantum state after each step \u2014 with automatic recognition of known states like Bell, GHZ, and W.",
  },
  {
    highlight: "bloch-sphere",
    tooltipSide: "left",
    title: "Bloch Sphere Panel",
    description: "This panel shows the quantum state on the Bloch sphere. Each qubit is a colored dot \u2014 the position tells you the qubit's state. North pole = |0\u27E9, south pole = |1\u27E9, equator = superposition.\n\nUse the Play button and timeline slider to step through the circuit.",
    onEnter: "resetBloch",
  },
  {
    highlight: "expand-bloch",
    tooltipSide: "left",
    title: "Expand for a Better View",
    description: "Click this button to open the Bloch sphere in a large fullscreen modal. Let's open it now to see the full experience.",
    onEnter: "openFullscreen",
  },
  {
    highlight: "modal-sphere",
    tooltipSide: "bottom",
    title: "The Bloch Sphere",
    description: "Here's the large Bloch sphere. Each colored dot represents one qubit. For the Bell state at step 0, both qubits start at the north pole (|0\u27E9).\n\nStep forward and watch: q0 moves to the equator (Hadamard creates superposition), then both dots collapse to the center (CNOT creates entanglement \u2014 individual qubits become maximally mixed).",
  },
  {
    highlight: "modal-controls",
    tooltipSide: "bottom",
    title: "Playback Controls",
    description: "Use these controls to explore the circuit:\n\n\u23EE Reset to start  |  \u23EA Step back  |  \u25B6 Play/Pause  |  \u23E9 Step forward\n\nDrag the timeline slider to scrub directly to any step. Adjust speed from 0.25x to 4x.\n\nTry stepping through now \u2014 watch how the Bloch vectors change at each gate!",
  },
  {
    highlight: "modal-correlation",
    tooltipSide: "bottom",
    title: "Entanglement Analysis",
    description: "Three tabs reveal the entanglement structure:\n\n\u0394Cov \u2014 measurement correlations between qubit pairs\nConcurrence \u2014 pairwise quantum entanglement (Wootters formula)\nTangle \u2014 genuinely multipartite entanglement (CKW)\n\nFor the Bell state, \u0394Cov shows +1.0 and concurrence is maximal. Click ? next to each tab for detailed explanations with examples.",
  },
  {
    highlight: "state-evolution",
    tooltipSide: "bottom",
    onEnter: "closeFullscreen",
    title: "Step-by-Step Explanations",
    description: "Every step gets a contextual explanation \u2014 not just what the gate does, but what it does to this specific state. The system detects when entanglement is created, when states become maximally mixed, and when you've built a recognized state.\n\nGreen badges appear when a known state (Bell, GHZ, W) is detected.",
  },
  {
    highlight: null,
    tooltipSide: "center",
    title: "Start Exploring!",
    description: "Try these:\n\n1. Press Play on the Bloch sphere and watch the Bell state form\n2. Load the GHZ preset and compare the Tangle tab (it'll be 1.0 \u2014 purely multipartite!)\n3. Load the W state and see the tangle drop to 0 while concurrence lights up\n4. Switch to Direct State mode and load ideal states to verify the math\n5. Build your own circuit from scratch and watch the narratives explain each step\n\nHave fun!",
  },
];

interface OnboardingOverlayProps {
  actions?: OnboardingActions;
}

export default function OnboardingOverlay({ actions }: OnboardingOverlayProps) {
  const [visible, setVisible] = useState(false);
  const [step, setStep] = useState(0);
  const [highlightRect, setHighlightRect] = useState<DOMRect | null>(null);
  const rafRef = useRef(0);

  useEffect(() => {
    try {
      const seen = localStorage.getItem(STORAGE_KEY);
      if (!seen) setVisible(true);
    } catch { /* noop */ }
  }, []);

  // Measure the highlighted element
  const updateHighlight = useCallback(() => {
    const current = STEPS[step];
    if (!current.highlight) {
      setHighlightRect(null);
      return;
    }
    const el = document.querySelector(`[data-onboarding="${current.highlight}"]`);
    if (el) {
      setHighlightRect(el.getBoundingClientRect());
    } else {
      setHighlightRect(null);
    }
  }, [step]);

  useEffect(() => {
    if (!visible) return;
    updateHighlight();
    // Re-measure on scroll/resize
    const handleUpdate = () => { rafRef.current = requestAnimationFrame(updateHighlight); };
    window.addEventListener("resize", handleUpdate);
    window.addEventListener("scroll", handleUpdate, true);
    return () => {
      window.removeEventListener("resize", handleUpdate);
      window.removeEventListener("scroll", handleUpdate, true);
      cancelAnimationFrame(rafRef.current);
    };
  }, [visible, step, updateHighlight]);

  // Run step action on enter
  useEffect(() => {
    if (!visible || !actions) return;
    const current = STEPS[step];
    if (current.onEnter && actions[current.onEnter]) {
      // Small delay so the UI has time to render
      const t = setTimeout(() => actions[current.onEnter!](), 100);
      return () => clearTimeout(t);
    }
  }, [visible, step, actions]);

  const dismiss = useCallback(() => {
    setVisible(false);
    try { localStorage.setItem(STORAGE_KEY, "true"); } catch { /* noop */ }
  }, []);

  const next = useCallback(() => {
    if (step < STEPS.length - 1) setStep((s) => s + 1);
    else dismiss();
  }, [step, dismiss]);

  const prev = useCallback(() => {
    if (step > 0) setStep((s) => s - 1);
  }, [step]);

  // Keyboard
  useEffect(() => {
    if (!visible) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") dismiss();
      if (e.key === "ArrowRight" || e.key === "Enter") next();
      if (e.key === "ArrowLeft") prev();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [visible, next, prev, dismiss]);

  if (!visible) return null;

  const current = STEPS[step];
  const isFirst = step === 0;
  const isLast = step === STEPS.length - 1;
  const hasHighlight = highlightRect !== null;
  const pad = 8; // padding around highlighted element

  // When highlighting inside the fullscreen modal, the dark overlay must sit
  // behind the modal (z-index 9998) so the modal content is visible,
  // while the tooltip stays on top (z-index 10001).
  const isModalStep = current.highlight?.startsWith("modal-") ?? false;
  const overlayZ = isModalStep ? 9998 : 10000;
  const tooltipZ = 10001;

  // Viewport-safe margins: keep tooltip away from edges and tab bar
  const MARGIN = 16;
  const TAB_BAR_HEIGHT = 60;
  const maxTop = window.innerHeight - TAB_BAR_HEIGHT;

  // Compute tooltip position, clamped to viewport
  const tooltipStyle = (): React.CSSProperties => {
    const maxW = 360;
    const estimatedH = 300; // rough tooltip height for clamping

    if (!hasHighlight || current.tooltipSide === "center") {
      return {
        position: "fixed",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        maxWidth: maxW,
      };
    }

    // For modal steps: position beside the modal, not overlapping it
    if (isModalStep) {
      const r = highlightRect!;
      // Find the modal container (parent of the highlighted element)
      const modalEl = document.querySelector("[data-onboarding='modal-sphere']")?.closest("[style*='min-height']")?.parentElement;
      const modalRect = modalEl?.getBoundingClientRect();
      if (modalRect) {
        // Place tooltip to the right of the modal if space, else below
        const spaceRight = window.innerWidth - modalRect.right;
        if (spaceRight > maxW + MARGIN * 2) {
          return {
            position: "fixed",
            top: Math.max(MARGIN, modalRect.top + 40),
            left: modalRect.right + MARGIN,
            maxWidth: Math.min(maxW, spaceRight - MARGIN * 2),
            maxHeight: maxTop - MARGIN * 2,
            overflowY: "auto" as const,
          };
        }
        // Place below the modal
        return {
          position: "fixed",
          top: Math.max(MARGIN, Math.min(modalRect.bottom + MARGIN, maxTop - estimatedH)),
          left: Math.max(MARGIN, modalRect.left),
          maxWidth: Math.min(maxW, modalRect.width),
          maxHeight: maxTop - modalRect.bottom - MARGIN * 2,
          overflowY: "auto" as const,
        };
      }
    }

    const r = highlightRect!;
    let top: number;
    let left: number | undefined;
    let right: number | undefined;

    switch (current.tooltipSide) {
      case "bottom":
        top = r.bottom + pad + 12;
        left = Math.max(MARGIN, Math.min(r.left, window.innerWidth - maxW - MARGIN));
        break;
      case "right":
        top = r.top;
        left = Math.min(r.right + pad + 12, window.innerWidth - maxW - MARGIN);
        break;
      case "left":
        top = r.top;
        right = Math.max(MARGIN, window.innerWidth - r.left + pad + 12);
        break;
      default:
        top = r.top;
        left = r.right + pad + 12;
    }

    // Clamp top: don't go above viewport or below tab bar
    top = Math.max(MARGIN, Math.min(top, maxTop - estimatedH));

    // Clamp left if set
    if (left !== undefined) {
      left = Math.max(MARGIN, Math.min(left, window.innerWidth - maxW - MARGIN));
    }

    return {
      position: "fixed",
      top,
      ...(left !== undefined ? { left } : {}),
      ...(right !== undefined ? { right } : {}),
      maxWidth: maxW,
      maxHeight: maxTop - top - MARGIN,
      overflowY: "auto" as const,
    };
  };

  // Tooltip is rendered as a sibling (not child) of the overlay so it's never
  // trapped inside a lower z-index stacking context during modal steps.
  return (
    <>
    {/* Overlay layer: dark background + spotlight */}
    {!isModalStep && (
    <div style={{ position: "fixed", inset: 0, zIndex: overlayZ }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "rgba(0, 0, 0, 0.75)",
          transition: "clip-path 0.3s ease",
          clipPath: hasHighlight
            ? `polygon(
                0% 0%, 0% 100%, 100% 100%, 100% 0%, 0% 0%,
                ${highlightRect!.left - pad}px ${highlightRect!.top - pad}px,
                ${highlightRect!.right + pad}px ${highlightRect!.top - pad}px,
                ${highlightRect!.right + pad}px ${highlightRect!.bottom + pad}px,
                ${highlightRect!.left - pad}px ${highlightRect!.bottom + pad}px,
                ${highlightRect!.left - pad}px ${highlightRect!.top - pad}px
              )`
            : undefined,
        }}
        onClick={(e) => { if (e.target === e.currentTarget) dismiss(); }}
      />

      {/* Highlight border glow — extra bright + pulsing for the expand button */}
      {hasHighlight && (
        <>
          {/* Inject pulse animation for expand button step */}
          {current.highlight === "expand-bloch" && (
            <style>{`
              @keyframes onboarding-pulse {
                0%, 100% { box-shadow: 0 0 20px ${colors.accent}, 0 0 40px ${colors.accent}80, 0 0 60px ${colors.accent}40; }
                50% { box-shadow: 0 0 30px ${colors.accent}, 0 0 60px ${colors.accent}a0, 0 0 90px ${colors.accent}60; }
              }
              @keyframes onboarding-pointer {
                0%, 100% { transform: translate(0, 0); }
                50% { transform: translate(-4px, -4px); }
              }
            `}</style>
          )}
          <div style={{
            position: "fixed",
            left: highlightRect!.left - pad,
            top: highlightRect!.top - pad,
            width: highlightRect!.width + pad * 2,
            height: highlightRect!.height + pad * 2,
            border: current.highlight === "expand-bloch"
              ? `3px solid #fff`
              : `2px solid ${colors.accent}`,
            borderRadius: current.highlight === "expand-bloch" ? 8 : 10,
            boxShadow: current.highlight === "expand-bloch"
              ? `0 0 20px ${colors.accent}, 0 0 40px ${colors.accent}80, 0 0 60px ${colors.accent}40`
              : `0 0 20px ${colors.accent}40, inset 0 0 20px ${colors.accent}10`,
            background: current.highlight === "expand-bloch" ? `${colors.accent}30` : undefined,
            animation: current.highlight === "expand-bloch" ? "onboarding-pulse 1.5s ease-in-out infinite" : undefined,
            pointerEvents: "none",
            transition: "all 0.3s ease",
          }} />
          {/* Click pointer for expand button — clamped to viewport */}
          {current.highlight === "expand-bloch" && (
            <div style={{
              position: "fixed",
              left: Math.min(highlightRect!.right + 4, window.innerWidth - 40),
              top: Math.min(highlightRect!.bottom + 4, window.innerHeight - 80),
              fontSize: 24,
              pointerEvents: "none",
              animation: "onboarding-pointer 1s ease-in-out infinite",
              filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.5))",
            }}>
              {"\uD83D\uDC46"}
            </div>
          )}
        </>
      )}
    </div>
    )}

      {/* Tooltip card — rendered at root level, always on top */}
      <div style={{
        ...tooltipStyle(),
        background: colors.bg,
        border: `1px solid ${colors.accent}80`,
        borderRadius: 12,
        padding: 24,
        boxShadow: `0 0 40px ${colors.accent}20, 0 20px 60px rgba(0,0,0,0.5)`,
        zIndex: tooltipZ,
      }}>
        {/* Step indicator */}
        <div style={{
          display: "flex",
          gap: 4,
          marginBottom: 16,
          justifyContent: "center",
        }}>
          {STEPS.map((_, i) => (
            <div
              key={i}
              style={{
                width: i === step ? 20 : 6,
                height: 6,
                borderRadius: 3,
                background: i === step ? colors.accent : i < step ? colors.accentDim : colors.border,
                transition: "all 0.2s ease",
                cursor: "pointer",
              }}
              onClick={() => setStep(i)}
            />
          ))}
        </div>

        <h3 style={{
          margin: "0 0 10px",
          fontSize: 18,
          fontWeight: 700,
          color: colors.text,
          fontFamily: fonts.sans,
        }}>
          {current.title}
        </h3>

        <p style={{
          margin: "0 0 20px",
          fontSize: 13,
          lineHeight: 1.7,
          color: colors.textSecondary,
          fontFamily: fonts.sans,
          whiteSpace: "pre-line",
        }}>
          {current.description}
        </p>

        {/* Step counter */}
        <div style={{
          fontSize: 10,
          color: colors.textTertiary,
          textAlign: "center",
          marginBottom: 12,
          fontFamily: fonts.mono,
        }}>
          {step + 1} / {STEPS.length}
        </div>

        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}>
          <div>
            {!isFirst && (
              <button onClick={prev} style={btnStyle(false)}>
                {"\u2190"} Back
              </button>
            )}
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {!isLast && (
              <button onClick={dismiss} style={btnSkipStyle}>
                Skip tour
              </button>
            )}
            <button onClick={next} style={btnStyle(true)}>
              {isLast ? "Get Started" : `Next ${"\u2192"}`}
            </button>
          </div>
        </div>

        <div style={{
          marginTop: 10,
          textAlign: "center",
          fontSize: 10,
          color: colors.textTertiary,
          fontFamily: fonts.sans,
        }}>
          Esc to skip {"\u00B7"} Arrow keys to navigate
        </div>
      </div>
    </>
  );
}

const btnStyle = (primary: boolean): React.CSSProperties => ({
  background: primary ? colors.accent : "transparent",
  color: primary ? "#fff" : colors.textSecondary,
  border: primary ? "none" : `1px solid ${colors.border}`,
  borderRadius: 6,
  padding: "7px 18px",
  fontSize: 12,
  fontWeight: 600,
  fontFamily: fonts.sans,
  cursor: "pointer",
});

const btnSkipStyle: React.CSSProperties = {
  background: "transparent",
  color: colors.textTertiary,
  border: "none",
  padding: "7px 14px",
  fontSize: 12,
  fontFamily: fonts.sans,
  cursor: "pointer",
};

/** Button to re-trigger the onboarding tour */
export function OnboardingResetButton() {
  const handleReset = () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      window.location.reload();
    } catch { /* noop */ }
  };

  return (
    <button
      onClick={handleReset}
      title="Show guided tour"
      style={{
        background: "transparent",
        color: colors.textTertiary,
        border: `1px solid ${colors.border}`,
        borderRadius: 6,
        padding: "6px 10px",
        fontSize: 11,
        fontFamily: fonts.sans,
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        gap: 4,
      }}
    >
      ? Tour
    </button>
  );
}
