'use dom';

import { useEffect, useRef, useMemo, useState } from "react";
import * as THREE from "three";
import { V3, TAU, spherePoints, statePoints, blochToThree } from "../math";
import type { ProbeStateConfig, RuntimeChannel } from "../types";
import type { BlochDot } from "../data/stateBlochConfigs";

// ── Mode-discriminated props ────────────────────────────────────

interface GlossaryMode {
  mode: "glossary";
  dots: BlochDot[];
  caption?: string;
  size?: number;
  expandable?: boolean;
}

interface VisualizerMode {
  mode: "visualizer";
  runtimeCh: Record<string, RuntimeChannel>;
  channel: string;
  strength: number;
  showOrig: boolean;
  showTrans: boolean;
  rotation: number;
  stateCfg: ProbeStateConfig;
  viewMode: "full" | "state";
  experimentMode?: boolean;
  additionalStates?: { bloch: { rx: number; ry: number; rz: number }; color: string; label: string }[];
}

interface CircuitMode {
  mode: "circuit";
  dots: BlochDot[];
  size?: number;
  /** Camera zoom: 1.0 = default, < 1 = zoomed in, > 1 = zoomed out */
  zoom?: number;
}

export type UnifiedBlochSphereProps = GlossaryMode | VisualizerMode | CircuitMode;

// ── Text sprite helper ──────────────────────────────────────────

function makeTextSprite(text: string, color: string, size = 0.12): THREE.Sprite {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 64;
  const ctx = canvas.getContext("2d")!;
  ctx.font = "bold 32px -apple-system, BlinkMacSystemFont, sans-serif";
  ctx.fillStyle = color;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, 64, 32);
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  const mat = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false });
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(size * 4, size * 2, 1);
  return sprite;
}

// ── Shared scaffold builder ─────────────────────────────────────

function buildScaffold(scene: THREE.Scene, opts: { background: number; detail: "full" | "mini" }) {
  scene.background = new THREE.Color(opts.background);

  // Wireframe sphere
  const segments = opts.detail === "full" ? 28 : 24;
  scene.add(new THREE.Mesh(
    new THREE.SphereGeometry(1, segments, segments === 28 ? 20 : 16),
    new THREE.MeshBasicMaterial({ color: 0x2a3a5a, wireframe: true, transparent: true, opacity: opts.detail === "full" ? 0.12 : 0.25 }),
  ));

  // Equator ring (mini mode only — full mode uses great circles)
  if (opts.detail === "mini") {
    const eqGeo = new THREE.RingGeometry(0.99, 1.01, 48);
    const eqMat = new THREE.MeshBasicMaterial({ color: 0x475569, transparent: true, opacity: 0.2, side: THREE.DoubleSide });
    const eqRing = new THREE.Mesh(eqGeo, eqMat);
    eqRing.rotation.x = Math.PI / 2;
    scene.add(eqRing);
  }

  // Axes
  const axColors = opts.detail === "full" ? [0xff4466, 0x44ff88, 0x4488ff] : [0x475569, 0x475569, 0x475569];
  const axLen = opts.detail === "full" ? 1.3 : 1.25;
  const axOpacity = opts.detail === "full" ? 0.35 : 0.35;
  [V3(1, 0, 0), V3(0, 1, 0), V3(0, 0, 1)].forEach((d, i) => {
    scene.add(new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([d.clone().multiplyScalar(-axLen), d.clone().multiplyScalar(axLen)]),
      new THREE.LineBasicMaterial({ color: axColors[i], transparent: true, opacity: axOpacity }),
    ));
  });

  // Pole dots (full mode only)
  if (opts.detail === "full") {
    const axC = [0xff4466, 0x44ff88, 0x4488ff];
    [V3(0, 0, 1.05), V3(0, 0, -1.05), V3(1.05, 0, 0), V3(-1.05, 0, 0), V3(0, 1.05, 0), V3(0, -1.05, 0)].forEach((pos, i) => {
      const m = new THREE.Mesh(
        new THREE.SphereGeometry(0.025, 8, 8),
        new THREE.MeshBasicMaterial({ color: axC[Math.floor(i / 2)] }),
      );
      m.position.copy(blochToThree(pos.x, pos.y, pos.z));
      scene.add(m);
    });

    // Axis labels + pole labels
    const labelData: [number, number, number, string, string][] = [
      [1.45, 0, 0, "X", "#ff4466"],    // +X axis
      [-1.45, 0, 0, "-X", "#ff4466"],
      [0, 1.45, 0, "Y", "#44ff88"],    // +Y axis
      [0, -1.45, 0, "-Y", "#44ff88"],
      [0, 0, 1.25, "|0\u27E9", "#4488ff"],  // +Z = |0⟩ (north pole)
      [0, 0, -1.25, "|1\u27E9", "#4488ff"],  // -Z = |1⟩ (south pole)
    ];
    for (const [bx, by, bz, text, color] of labelData) {
      const sprite = makeTextSprite(text, color, text.length > 2 ? 0.14 : 0.1);
      sprite.position.copy(blochToThree(bx, by, bz));
      scene.add(sprite);
    }

    // Great circles
    [0, 1, 2].forEach((ax) => {
      const cp: THREE.Vector3[] = [];
      for (let i = 0; i <= 64; i++) {
        const a = (i / 64) * TAU;
        if (ax === 0) cp.push(V3(Math.cos(a), Math.sin(a), 0));
        else if (ax === 1) cp.push(V3(Math.cos(a), 0, Math.sin(a)));
        else cp.push(V3(0, Math.cos(a), Math.sin(a)));
      }
      scene.add(new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(cp),
        new THREE.LineBasicMaterial({ color: 0x2a3a5a, transparent: true, opacity: 0.12 }),
      ));
    });

    // Lighting
    scene.add(new THREE.AmbientLight(0x404060, 0.8));
    const dl = new THREE.DirectionalLight(0xffffff, 0.6);
    dl.position.set(3, 4, 2);
    scene.add(dl);
  }
}

// ── Add dot meshes to scene ─────────────────────────────────────

function addDotMeshes(
  scene: THREE.Scene,
  dots: BlochDot[],
  opts: { glow: boolean; dotSize: number },
): THREE.Mesh[] {
  const meshes: THREE.Mesh[] = [];
  for (const d of dots) {
    const dotGeo = new THREE.SphereGeometry(opts.dotSize, 16, 12);
    const dotMat = new THREE.MeshBasicMaterial({ color: d.color });
    const dot = new THREE.Mesh(dotGeo, dotMat);
    dot.position.copy(blochToThree(d.rx, d.ry, d.rz));
    scene.add(dot);
    meshes.push(dot);

    if (opts.glow) {
      const glowGeo = new THREE.SphereGeometry(opts.dotSize * 1.875, 16, 12);
      const glowMat = new THREE.MeshBasicMaterial({ color: d.color, transparent: true, opacity: 0.15 });
      const glow = new THREE.Mesh(glowGeo, glowMat);
      glow.position.copy(dot.position);
      scene.add(glow);
    }
  }
  return meshes;
}

// ── Main component ──────────────────────────────────────────────

export default function UnifiedBlochSphere(props: UnifiedBlochSphereProps) {
  if (props.mode === "glossary") return <GlossarySphere {...props} />;
  if (props.mode === "visualizer") return <VisualizerSphere {...props} />;
  return <CircuitSphere {...props} />;
}

// ── Glossary mode ───────────────────────────────────────────────

function GlossarySphere({ dots, caption, size = 120, expandable = true }: GlossaryMode) {
  const [expanded, setExpanded] = useState(false);
  const mountRef = useRef<HTMLDivElement>(null);
  const frameRef = useRef(0);
  const autoRotateRef = useRef(true);
  const currentSize = expanded ? 280 : size;

  useEffect(() => {
    const el = mountRef.current;
    if (!el) return;
    while (el.firstChild) el.removeChild(el.firstChild);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
    camera.position.set(2.5, 1.8, 2.5);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(currentSize, currentSize);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    el.appendChild(renderer.domElement);

    buildScaffold(scene, { background: 0x000000, detail: "mini" });
    addDotMeshes(scene, dots, { glow: true, dotSize: 0.08 });

    autoRotateRef.current = true;

    // Drag to spin
    let dragging = false;
    let prevX = 0;
    const canvas = renderer.domElement;

    const onDown = (e: PointerEvent) => { dragging = true; prevX = e.clientX; autoRotateRef.current = false; canvas.style.cursor = "grabbing"; };
    const onMove = (e: PointerEvent) => { if (!dragging) return; scene.rotation.y += (e.clientX - prevX) * 0.012; prevX = e.clientX; };
    const onUp = () => { dragging = false; canvas.style.cursor = "grab"; };

    canvas.addEventListener("pointerdown", onDown);
    canvas.addEventListener("pointermove", onMove);
    canvas.addEventListener("pointerup", onUp);
    canvas.addEventListener("pointerleave", onUp);
    canvas.style.cursor = "grab";

    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);
      if (autoRotateRef.current) scene.rotation.y += 0.004;
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(frameRef.current);
      canvas.removeEventListener("pointerdown", onDown);
      canvas.removeEventListener("pointermove", onMove);
      canvas.removeEventListener("pointerup", onUp);
      canvas.removeEventListener("pointerleave", onUp);
      renderer.dispose();
    };
  }, [dots, currentSize]);

  return (
    <div
      style={{
        display: "flex", flexDirection: "column", alignItems: "center",
        justifyContent: "center", padding: 4, cursor: expandable ? "pointer" : "default",
        transition: "all 0.25s ease",
      }}
      onClick={expandable ? (e) => { e.stopPropagation(); setExpanded((v) => !v); } : undefined}
      title={expandable ? (expanded ? "Click to shrink" : "Click to expand") : undefined}
    >
      <div ref={mountRef} style={{ width: currentSize, height: currentSize, transition: "width 0.25s ease, height 0.25s ease" }} />
      <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 3 }}>
        {caption && (
          <span style={{ color: "#64748b", fontSize: expanded ? 10 : 8, fontFamily: "-apple-system, BlinkMacSystemFont, sans-serif", transition: "font-size 0.2s ease" }}>
            {caption}
          </span>
        )}
        {expandable && (
          <span style={{ color: "#4f46e5", fontSize: 8, fontFamily: "-apple-system, BlinkMacSystemFont, sans-serif", opacity: 0.7 }}>
            {expanded ? "\u25BE shrink" : "\u25B8 expand"}
          </span>
        )}
      </div>
    </div>
  );
}

// ── Visualizer mode ─────────────────────────────────────────────

function VisualizerSphere({
  runtimeCh, channel, strength, showOrig, showTrans, rotation,
  stateCfg, viewMode, experimentMode = false, additionalStates,
}: VisualizerMode) {
  const mountRef = useRef<HTMLDivElement>(null);
  const frameRef = useRef<number>(0);

  const pRef = useRef({ rotation, channel, strength, showOrig, showTrans, experimentMode });
  useEffect(() => { pRef.current = { rotation, channel, strength, showOrig, showTrans, experimentMode }; });
  const chRef = useRef(runtimeCh);
  useEffect(() => { chRef.current = runtimeCh; }, [runtimeCh]);

  const origPts = useMemo(() => {
    return viewMode === "state" ? statePoints(stateCfg, 350) : spherePoints(350);
  }, [stateCfg, viewMode]);
  const origPtsRef = useRef(origPts);
  useEffect(() => { origPtsRef.current = origPts; }, [origPts]);

  const key = `${viewMode}-${stateCfg?.name}-${JSON.stringify(stateCfg?.bloch)}-${experimentMode}-${additionalStates?.length ?? 0}`;

  useEffect(() => {
    const el = mountRef.current;
    if (!el) return;
    const w = el.clientWidth, h = el.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 100);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    el.appendChild(renderer.domElement);

    buildScaffold(scene, { background: 0x08090e, detail: "full" });

    // Additional state dots (experiment "All qubits" view)
    if (additionalStates?.length) {
      for (const st of additionalStates) {
        const m = new THREE.Mesh(
          new THREE.SphereGeometry(0.06, 12, 12),
          new THREE.MeshBasicMaterial({ color: new THREE.Color(st.color) }),
        );
        m.position.copy(blochToThree(st.bloch.rx, st.bloch.ry, st.bloch.rz));
        scene.add(m);
      }
    }

    // State Bloch vector arrow
    const bv = stateCfg?.bloch ?? { rx: 0, ry: 0, rz: 0 };
    const bLen = Math.sqrt(bv.rx * bv.rx + bv.ry * bv.ry + bv.rz * bv.rz);
    if (bLen > 0.05) {
      const dir = blochToThree(bv.rx, bv.ry, bv.rz);
      const stColor = new THREE.Color(stateCfg.color ?? "#ffffff");
      scene.add(new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([V3(0, 0, 0), dir.clone().normalize().multiplyScalar(bLen)]),
        new THREE.LineBasicMaterial({ color: stColor, linewidth: 2, transparent: true, opacity: 0.8 }),
      ));
      const tipMesh = new THREE.Mesh(
        new THREE.SphereGeometry(0.04, 8, 8),
        new THREE.MeshBasicMaterial({ color: stColor }),
      );
      tipMesh.position.copy(dir.clone().normalize().multiplyScalar(bLen));
      scene.add(tipMesh);
    }

    // Point clouds
    const pts = origPtsRef.current;
    const mkCloud = (color: number, size: number, opacity: number): THREE.Points => {
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pts.length * 3), 3));
      const c = new THREE.Points(g, new THREE.PointsMaterial({ color, size, transparent: true, opacity }));
      scene.add(c);
      return c;
    };
    const origCloud = mkCloud(0x3366aa, 0.018, 0.3);
    const transCloud = mkCloud(0xff9933, 0.022, 0.65);

    // Set initial positions for original cloud
    const op = origCloud.geometry.attributes.position.array as Float32Array;
    pts.forEach((p, i) => {
      op[i * 3] = p.x;
      op[i * 3 + 1] = p.z;
      op[i * 3 + 2] = p.y;
    });
    origCloud.geometry.attributes.position.needsUpdate = true;

    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);
      const pr = pRef.current;
      camera.position.set(2.8 * Math.cos(pr.rotation), 1.4, 2.8 * Math.sin(pr.rotation));
      camera.lookAt(0, 0, 0);

      if (pr.experimentMode) {
        transCloud.visible = false;
        origCloud.visible = pr.showOrig;
      } else {
        const ch = chRef.current[pr.channel];
        const curPts = origPtsRef.current;
        if (ch && curPts) {
          const pos = transCloud.geometry.attributes.position.array as Float32Array;
          curPts.forEach((pt, i) => {
            const t = ch.apply(pt, pr.strength);
            pos[i * 3] = t.x;
            pos[i * 3 + 1] = t.z;
            pos[i * 3 + 2] = t.y;
          });
          transCloud.geometry.attributes.position.needsUpdate = true;
        }
        transCloud.visible = pr.showTrans;
        origCloud.visible = pr.showOrig;
      }
      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!el) return;
      const nw = el.clientWidth, nh = el.clientHeight;
      camera.aspect = nw / nh;
      camera.updateProjectionMatrix();
      renderer.setSize(nw, nh);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(frameRef.current);
      renderer.dispose();
      if (el.contains(renderer.domElement)) el.removeChild(renderer.domElement);
    };
  }, [key]);

  return (
    <div ref={mountRef} style={{ width: "100%", height: "100%", borderRadius: "8px", overflow: "hidden" }} />
  );
}

// ── Circuit mode ────────────────────────────────────────────────

function CircuitSphere({ dots, size, zoom = 1 }: CircuitMode) {
  const mountRef = useRef<HTMLDivElement>(null);
  const frameRef = useRef<number>(0);
  const dotsRef = useRef(dots);
  useEffect(() => { dotsRef.current = dots; }, [dots]);
  const zoomRef = useRef(zoom);
  useEffect(() => { zoomRef.current = zoom; }, [zoom]);

  const dotMeshesRef = useRef<THREE.Mesh[]>([]);
  const glowMeshesRef = useRef<THREE.Mesh[]>([]);

  // Rebuild key based on number of dots (add/remove qubits)
  const key = dots.length;

  useEffect(() => {
    const el = mountRef.current;
    if (!el) return;
    while (el.firstChild) el.removeChild(el.firstChild);

    const renderSize = size ?? (Math.min(el.clientWidth, el.clientHeight) || 280);
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
    camera.position.set(2.5, 1.8, 2.5);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(renderSize, renderSize);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x08090e, 1);
    el.appendChild(renderer.domElement);

    buildScaffold(scene, { background: 0x08090e, detail: "full" });

    // Create dot + glow meshes for each qubit
    const currentDots = dotsRef.current;
    const dotMeshes: THREE.Mesh[] = [];
    const glowMeshes: THREE.Mesh[] = [];
    for (const d of currentDots) {
      const dotGeo = new THREE.SphereGeometry(0.07, 16, 12);
      const dotMat = new THREE.MeshBasicMaterial({ color: d.color });
      const dot = new THREE.Mesh(dotGeo, dotMat);
      dot.position.copy(blochToThree(d.rx, d.ry, d.rz));
      scene.add(dot);
      dotMeshes.push(dot);

      const glowGeo = new THREE.SphereGeometry(0.14, 16, 12);
      const glowMat = new THREE.MeshBasicMaterial({ color: d.color, transparent: true, opacity: 0.2 });
      const glow = new THREE.Mesh(glowGeo, glowMat);
      glow.position.copy(dot.position);
      scene.add(glow);
      glowMeshes.push(glow);
    }
    dotMeshesRef.current = dotMeshes;
    glowMeshesRef.current = glowMeshes;

    const baseDistance = 3.5;
    const autoRotateRef = { current: true };

    // Drag-to-rotate
    let dragging = false;
    let prevX = 0;
    let prevY = 0;
    const canvas = renderer.domElement;

    const onDown = (e: PointerEvent) => {
      dragging = true;
      prevX = e.clientX;
      prevY = e.clientY;
      autoRotateRef.current = false;
      canvas.style.cursor = "grabbing";
    };
    const onMove = (e: PointerEvent) => {
      if (!dragging) return;
      scene.rotation.y += (e.clientX - prevX) * 0.01;
      scene.rotation.x += (e.clientY - prevY) * 0.01;
      // Clamp vertical rotation
      scene.rotation.x = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, scene.rotation.x));
      prevX = e.clientX;
      prevY = e.clientY;
    };
    const onUp = () => {
      dragging = false;
      canvas.style.cursor = "grab";
    };

    canvas.addEventListener("pointerdown", onDown);
    canvas.addEventListener("pointermove", onMove);
    canvas.addEventListener("pointerup", onUp);
    canvas.addEventListener("pointerleave", onUp);
    canvas.style.cursor = "grab";

    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);
      // Gentle auto-rotate (paused during drag)
      if (autoRotateRef.current) scene.rotation.y += 0.002;

      // Apply zoom to camera distance
      const z = zoomRef.current;
      const dist = baseDistance * z;
      camera.position.set(dist * 0.72, dist * 0.52, dist * 0.72);
      camera.lookAt(0, 0, 0);

      // Update dot positions from ref (no scene rebuild needed)
      const curDots = dotsRef.current;
      for (let i = 0; i < dotMeshes.length && i < curDots.length; i++) {
        const pos = blochToThree(curDots[i].rx, curDots[i].ry, curDots[i].rz);
        dotMeshes[i].position.copy(pos);
        glowMeshes[i].position.copy(pos);
      }

      renderer.render(scene, camera);
    };
    animate();

    return () => {
      canvas.removeEventListener("pointerdown", onDown);
      canvas.removeEventListener("pointermove", onMove);
      canvas.removeEventListener("pointerup", onUp);
      canvas.removeEventListener("pointerleave", onUp);
      cancelAnimationFrame(frameRef.current);
      renderer.dispose();
    };
  }, [key, size]);

  return (
    <div ref={mountRef} style={{ width: size ?? "100%", height: size ?? "100%", borderRadius: "8px", overflow: "hidden" }} />
  );
}
