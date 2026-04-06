'use dom';

/** Simple MI matrix heatmap for experiment mode PTM tab */
export default function MIMatrixHeatmap({ matrix }: { matrix: number[][] }) {
  const n = matrix.length;
  const mx = Math.max(...matrix.flat().filter((_, i) => Math.floor(i / n) !== i % n), 0.01);

  return (
    <div>
      <div style={{ display: "flex", marginLeft: "28px" }}>
        {Array.from({ length: n }, (_, i) => (
          <div key={i} style={{
            width: "32px", textAlign: "center", fontSize: "9px",
            color: "#8899aa", fontFamily: "monospace", fontWeight: 600,
          }}>Q{i}</div>
        ))}
      </div>
      {matrix.map((row, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center" }}>
          <div style={{
            width: "28px", fontSize: "9px", textAlign: "right", paddingRight: "5px",
            color: "#8899aa", fontFamily: "monospace", fontWeight: 600,
          }}>Q{i}</div>
          {row.map((v, j) => (
            <div key={j} style={{
              width: "32px", height: "24px", display: "flex", alignItems: "center", justifyContent: "center",
              background: i === j ? "rgba(255,255,255,0.02)"
                : `rgba(68,200,255,${Math.min(v / mx * 0.7, 0.7)})`,
              borderRadius: "3px", margin: "1px",
              fontSize: "8px", fontFamily: "monospace",
              color: i === j ? "#334" : v / mx > 0.4 ? "#fff" : "#556",
            }}>
              {i === j ? "\u2014" : v.toFixed(2)}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
