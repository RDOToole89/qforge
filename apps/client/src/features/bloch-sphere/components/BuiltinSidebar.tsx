'use dom';

import { chrome, viz } from "@/src/design/tokens";
import type { BlochConfig, RuntimeChannel } from "../types";
import { LS, bdr, cS, cT } from "../styles";

interface BuiltinSidebarProps {
  config: BlochConfig;
  stateKey: string;
  setStateKey: (v: string) => void;
  channel: string;
  setChannel: (v: string) => void;
  runtimeCh: Record<string, RuntimeChannel>;
  tab: "single" | "multi" | "ptm" | "data";
  activeTopo: string;
  setActiveTopo: (v: string) => void;
  viewMode: "full" | "state";
  setViewMode: (v: "full" | "state") => void;
  showOrig: boolean;
  setShowOrig: (v: boolean) => void;
  showTrans: boolean;
  setShowTrans: (v: boolean) => void;
  strength: number;
  setStrength: (v: number) => void;
  animating: boolean;
  setAnimating: (v: boolean) => void;
  animRef: React.RefObject<number>;
  toggleAnim: () => void;
}

export default function BuiltinSidebar(props: BuiltinSidebarProps) {
  const {
    config, stateKey, setStateKey, channel, setChannel, runtimeCh,
    tab, activeTopo, setActiveTopo, viewMode, setViewMode,
    showOrig, setShowOrig, showTrans, setShowTrans,
    strength, setStrength, animating, setAnimating, animRef, toggleAnim,
  } = props;

  return (
    <>
      {/* STATE SELECTOR -- always visible */}
      <div>
        <div style={LS}>PROBE STATE</div>
        {Object.entries(config.states).map(([key, st]) => (
          <button key={key} onClick={() => setStateKey(key)} style={{
            display: "flex", width: "100%", padding: "5px 9px", marginBottom: "2px",
            alignItems: "center", gap: "7px",
            background: stateKey === key ? `${st.color ?? viz.orange}26` : chrome.border.subtle,
            border: stateKey === key ? `1px solid ${st.color ?? viz.orange}44` : bdr,
            borderRadius: "5px",
            color: stateKey === key ? (st.color ?? viz.orange) : chrome.text.tertiary,
            fontSize: "11.5px", fontFamily: "inherit", cursor: "pointer", textAlign: "left",
          }}>
            <span style={{
              display: "inline-block", width: "7px", height: "7px", borderRadius: "50%",
              background: st.color ?? chrome.text.tertiary, flexShrink: 0,
            }} />
            <span>
              <span style={{ fontWeight: 500 }}>{st.name}</span>
              {st.zBasisSignal && (
                <span style={{
                  marginLeft: "5px", fontSize: "9px", padding: "1px 5px", borderRadius: "3px",
                  background: st.zBasisSignal === "strong" ? `${viz.green}26`
                    : st.zBasisSignal === "weak" ? `${chrome.status.warning}26` : `${chrome.status.error}1f`,
                  color: st.zBasisSignal === "strong" ? viz.green
                    : st.zBasisSignal === "weak" ? chrome.status.warning : chrome.status.error,
                }}>
                  {st.zBasisSignal === "strong" ? "Z✓" : st.zBasisSignal === "weak" ? "Z~" : "Z✗"}
                </span>
              )}
            </span>
          </button>
        ))}
      </div>

      {/* CHANNEL SELECTOR */}
      {(tab === "single" || tab === "ptm") && (
        <div>
          <div style={LS}>CHANNEL</div>
          {Object.entries(runtimeCh).map(([key, val]) => (
            <button key={key} onClick={() => setChannel(key)} style={{
              display: "block", width: "100%", padding: "4px 9px", marginBottom: "2px",
              background: channel === key ? `${viz.orange}1f` : chrome.border.subtle,
              border: channel === key ? `1px solid ${viz.orange}4d` : bdr,
              borderRadius: "5px",
              color: channel === key ? viz.orange : chrome.text.tertiary,
              fontSize: "11px", fontFamily: "inherit", cursor: "pointer", textAlign: "left",
            }}>
              <span style={{ fontWeight: 500 }}>{val.name}</span>
              <span style={{ fontSize: "9.5px", opacity: 0.5, marginLeft: "5px" }}>{val.desc}</span>
            </button>
          ))}
        </div>
      )}

      {/* TOPOLOGY SELECTOR */}
      {tab === "multi" && (
        <div>
          <div style={LS}>TOPOLOGY</div>
          <button onClick={() => setActiveTopo("all")} style={{
            display: "block", width: "100%", padding: "4px 9px", marginBottom: "2px",
            background: activeTopo === "all" ? `${viz.orange}1f` : chrome.border.subtle,
            border: activeTopo === "all" ? `1px solid ${viz.orange}4d` : bdr,
            borderRadius: "5px",
            color: activeTopo === "all" ? viz.orange : chrome.text.tertiary,
            fontSize: "11px", fontFamily: "inherit", cursor: "pointer", textAlign: "left",
          }}>All</button>
          {Object.entries(config.topologies).map(([key, val]) => (
            <button key={key} onClick={() => setActiveTopo(key)} style={{
              display: "block", width: "100%", padding: "4px 9px", marginBottom: "2px",
              background: activeTopo === key ? `${viz.purple}1f` : chrome.border.subtle,
              border: activeTopo === key ? `1px solid ${viz.purple}4d` : bdr,
              borderRadius: "5px",
              color: activeTopo === key ? viz.purple : chrome.text.tertiary,
              fontSize: "11px", fontFamily: "inherit", cursor: "pointer", textAlign: "left",
            }}>{val.name}</button>
          ))}
        </div>
      )}

      {/* CONTROLS */}
      {tab !== "data" && (
        <>
          {tab === "single" && (
            <div style={{ display: "flex", gap: "4px" }}>
              <button onClick={() => setViewMode(viewMode === "full" ? "state" : "full")} style={{
                flex: 1, padding: "4px 8px", borderRadius: "5px",
                fontSize: "10px", fontFamily: "inherit", cursor: "pointer",
                background: viewMode === "state" ? `${viz.purple}26` : chrome.border.subtle,
                border: viewMode === "state" ? `1px solid ${viz.purple}4d` : bdr,
                color: viewMode === "state" ? viz.purple : chrome.text.tertiary,
              }}>
                {viewMode === "state" ? "◉ State View" : "○ Full Sphere"}
              </button>
              <button onClick={() => setShowOrig(!showOrig)} style={{
                padding: "4px 8px", borderRadius: "5px",
                fontSize: "10px", fontFamily: "inherit", cursor: "pointer",
                background: showOrig ? `${viz.blueDim}22` : chrome.border.subtle,
                border: showOrig ? `1px solid ${viz.blueDim}44` : bdr,
                color: showOrig ? viz.blueDim : chrome.text.tertiary,
              }}>{"●"}</button>
              <button onClick={() => setShowTrans(!showTrans)} style={{
                padding: "4px 8px", borderRadius: "5px",
                fontSize: "10px", fontFamily: "inherit", cursor: "pointer",
                background: showTrans ? `${viz.orange}22` : chrome.border.subtle,
                border: showTrans ? `1px solid ${viz.orange}44` : bdr,
                color: showTrans ? viz.orange : chrome.text.tertiary,
              }}>{"●"}</button>
            </div>
          )}

          <div>
            <div style={LS}>
              STRENGTH — <span style={{ color: viz.orange }}>{strength.toFixed(2)}</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.005"
              value={strength}
              onChange={(e) => {
                if (animating) { setAnimating(false); cancelAnimationFrame(animRef.current); }
                setStrength(parseFloat(e.target.value));
              }}
              style={{ width: "100%", accentColor: viz.orange }}
            />
          </div>

          <button onClick={toggleAnim} style={{
            padding: "5px 12px", borderRadius: "5px",
            fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
            background: animating ? `${viz.orange}33` : chrome.border.subtle,
            border: animating ? `1px solid ${viz.orange}66` : bdr,
            color: animating ? viz.orange : chrome.text.tertiary,
          }}>
            {animating ? "⏸ Pause" : "▶ Animate"}
          </button>
        </>
      )}

      <div style={cS(viz.blue)}>
        <div style={cT(viz.blue)}>CONTRACTIVITY</div>
        CPTP maps can only shrink or preserve the Bloch ball. Orange {"⊆"} Blue.
      </div>
    </>
  );
}
