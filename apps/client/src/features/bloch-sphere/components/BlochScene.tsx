'use dom';

import { useEffect, useRef, useMemo } from "react";
import * as THREE from "three";
import { V3, TAU, spherePoints, statePoints } from "../math";
import type { ProbeStateConfig, RuntimeChannel } from "../types";

interface BlochSceneProps {
  runtimeCh: Record<string, RuntimeChannel>;
  channel: string;
  strength: number;
  showOrig: boolean;
  showTrans: boolean;
  rotation: number;
  stateCfg: ProbeStateConfig;
  viewMode: "full" | "state";
}

export default function BlochScene({
  runtimeCh,
  channel,
  strength,
  showOrig,
  showTrans,
  rotation,
  stateCfg,
  viewMode,
}: BlochSceneProps) {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<{
    scene: THREE.Scene;
    camera: THREE.PerspectiveCamera;
    renderer: THREE.WebGLRenderer;
    origCloud: THREE.Points;
    transCloud: THREE.Points;
    el: HTMLDivElement;
  } | null>(null);
  const frameRef = useRef<number>(0);

  // Keep current props in refs for animation loop
  const pRef = useRef({ rotation, channel, strength, showOrig, showTrans });
  useEffect(() => {
    pRef.current = { rotation, channel, strength, showOrig, showTrans };
  });
  const chRef = useRef(runtimeCh);
  useEffect(() => { chRef.current = runtimeCh; }, [runtimeCh]);

  const origPts = useMemo(() => {
    return viewMode === "state" ? statePoints(stateCfg, 350) : spherePoints(350);
  }, [stateCfg, viewMode]);

  const origPtsRef = useRef(origPts);
  useEffect(() => { origPtsRef.current = origPts; }, [origPts]);

  // Remount key when view mode or state changes
  const key = `${viewMode}-${stateCfg?.name}-${JSON.stringify(stateCfg?.bloch)}`;

  useEffect(() => {
    const el = mountRef.current;
    if (!el) return;
    const w = el.clientWidth, h = el.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x08090e);
    const camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 100);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    el.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0x404060, 0.8));
    const dl = new THREE.DirectionalLight(0xffffff, 0.6);
    dl.position.set(3, 4, 2);
    scene.add(dl);

    // Wireframe sphere
    scene.add(new THREE.Mesh(
      new THREE.SphereGeometry(1, 28, 20),
      new THREE.MeshBasicMaterial({ color: 0x2a3a5a, wireframe: true, transparent: true, opacity: 0.12 }),
    ));

    // Axes
    const axC = [0xff4466, 0x44ff88, 0x4488ff];
    [V3(1, 0, 0), V3(0, 1, 0), V3(0, 0, 1)].forEach((d, i) => {
      scene.add(new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([d.clone().multiplyScalar(-1.3), d.clone().multiplyScalar(1.3)]),
        new THREE.LineBasicMaterial({ color: axC[i], transparent: true, opacity: 0.35 }),
      ));
    });

    // Pole dots
    [V3(0, 0, 1.05), V3(0, 0, -1.05), V3(1.05, 0, 0), V3(-1.05, 0, 0), V3(0, 1.05, 0), V3(0, -1.05, 0)].forEach((pos, i) => {
      const m = new THREE.Mesh(
        new THREE.SphereGeometry(0.025, 8, 8),
        new THREE.MeshBasicMaterial({ color: axC[Math.floor(i / 2)] }),
      );
      m.position.set(pos.x, pos.z, pos.y); // swap Y/Z for Three.js
      scene.add(m);
    });

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

    // State Bloch vector arrow
    const bv = stateCfg?.bloch ?? { rx: 0, ry: 0, rz: 0 };
    const bLen = Math.sqrt(bv.rx * bv.rx + bv.ry * bv.ry + bv.rz * bv.rz);
    if (bLen > 0.05) {
      const dir = V3(bv.rx, bv.rz, bv.ry); // swap Y/Z
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
      op[i * 3 + 1] = p.z; // Three.js Y = Bloch Z (up)
      op[i * 3 + 2] = p.y; // Three.js Z = Bloch Y
    });
    origCloud.geometry.attributes.position.needsUpdate = true;

    sceneRef.current = { scene, camera, renderer, origCloud, transCloud, el };

    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);
      const pr = pRef.current;
      camera.position.set(
        2.8 * Math.cos(pr.rotation),
        1.4,
        2.8 * Math.sin(pr.rotation),
      );
      camera.lookAt(0, 0, 0);

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
    <div
      ref={mountRef}
      style={{ width: "100%", height: "100%", borderRadius: "8px", overflow: "hidden" }}
    />
  );
}
