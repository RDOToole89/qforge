'use dom';

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
            background: stateKey === key ? `${st.color ?? "#ff9933"}18` : "rgba(255,255,255,0.02)",
            border: stateKey === key ? `1px solid ${st.color ?? "#ff9933"}44` : bdr,
            borderRadius: "5px",
            color: stateKey === key ? (st.color ?? "#ff9933") : "#667788",
            fontSize: "11.5px", fontFamily: "inherit", cursor: "pointer", textAlign: "left",
          }}>
            <span style={{
              display: "inline-block", width: "7px", height: "7px", borderRadius: "50%",
              background: st.color ?? "#888", flexShrink: 0,
            }} />
            <span>
              <span style={{ fontWeight: 500 }}>{st.name}</span>
              {st.zBasisSignal && (
                <span style={{
                  marginLeft: "5px", fontSize: "9px", padding: "1px 5px", borderRadius: "3px",
                  background: st.zBasisSignal === "strong" ? "rgba(68,255,136,0.15)"
                    : st.zBasisSignal === "weak" ? "rgba(255,200,50,0.15)" : "rgba(255,68,68,0.12)",
                  color: st.zBasisSignal === "strong" ? "#44ff88"
                    : st.zBasisSignal === "weak" ? "#dda030" : "#ff6666",
                }}>
                  {st.zBasisSignal === "strong" ? "Z\u2713" : st.zBasisSignal === "weak" ? "Z~" : "Z\u2717"}
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
              background: channel === key ? "rgba(255,153,51,0.12)" : "rgba(255,255,255,0.02)",
              border: channel === key ? "1px solid rgba(255,153,51,0.3)" : bdr,
              borderRadius: "5px",
              color: channel === key ? "#ff9933" : "#667788",
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
            background: activeTopo === "all" ? "rgba(255,153,51,0.12)" : "rgba(255,255,255,0.02)",
            border: activeTopo === "all" ? "1px solid rgba(255,153,51,0.3)" : bdr,
            borderRadius: "5px",
            color: activeTopo === "all" ? "#ff9933" : "#667788",
            fontSize: "11px", fontFamily: "inherit", cursor: "pointer", textAlign: "left",
          }}>All</button>
          {Object.entries(config.topologies).map(([key, val]) => (
            <button key={key} onClick={() => setActiveTopo(key)} style={{
              display: "block", width: "100%", padding: "4px 9px", marginBottom: "2px",
              background: activeTopo === key ? "rgba(180,140,255,0.12)" : "rgba(255,255,255,0.02)",
              border: activeTopo === key ? "1px solid rgba(180,140,255,0.3)" : bdr,
              borderRadius: "5px",
              color: activeTopo === key ? "#b48cff" : "#667788",
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
                background: viewMode === "state" ? "rgba(180,140,255,0.15)" : "rgba(255,255,255,0.02)",
                border: viewMode === "state" ? "1px solid rgba(180,140,255,0.3)" : bdr,
                color: viewMode === "state" ? "#b48cff" : "#556677",
              }}>
                {viewMode === "state" ? "\u25C9 State View" : "\u25CB Full Sphere"}
              </button>
              <button onClick={() => setShowOrig(!showOrig)} style={{
                padding: "4px 8px", borderRadius: "5px",
                fontSize: "10px", fontFamily: "inherit", cursor: "pointer",
                background: showOrig ? "#3366aa22" : "rgba(255,255,255,0.02)",
                border: showOrig ? "1px solid #3366aa44" : bdr,
                color: showOrig ? "#3366aa" : "#556677",
              }}>{"\u25CF"}</button>
              <button onClick={() => setShowTrans(!showTrans)} style={{
                padding: "4px 8px", borderRadius: "5px",
                fontSize: "10px", fontFamily: "inherit", cursor: "pointer",
                background: showTrans ? "#ff993322" : "rgba(255,255,255,0.02)",
                border: showTrans ? "1px solid #ff993344" : bdr,
                color: showTrans ? "#ff9933" : "#556677",
              }}>{"\u25CF"}</button>
            </div>
          )}

          <div>
            <div style={LS}>
              STRENGTH — <span style={{ color: "#ff9933" }}>{strength.toFixed(2)}</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.005"
              value={strength}
              onChange={(e) => {
                if (animating) { setAnimating(false); cancelAnimationFrame(animRef.current); }
                setStrength(parseFloat(e.target.value));
              }}
              style={{ width: "100%", accentColor: "#ff9933" }}
            />
          </div>

          <button onClick={toggleAnim} style={{
            padding: "5px 12px", borderRadius: "5px",
            fontSize: "11px", fontFamily: "inherit", cursor: "pointer",
            background: animating ? "rgba(255,153,51,0.2)" : "rgba(255,255,255,0.04)",
            border: animating ? "1px solid rgba(255,153,51,0.4)" : bdr,
            color: animating ? "#ff9933" : "#667788",
          }}>
            {animating ? "\u23F8 Pause" : "\u25B6 Animate"}
          </button>
        </>
      )}

      <div style={cS("rgba(68,136,255)")}>
        <div style={cT("#4488ff")}>CONTRACTIVITY</div>
        CPTP maps can only shrink or preserve the Bloch ball. Orange {"\u2286"} Blue.
      </div>
    </>
  );
}
