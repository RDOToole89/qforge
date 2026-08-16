'use dom';

import { useEffect, useRef, useMemo } from "react";
import * as THREE from "three";
import { chrome } from "@/src/design/tokens";
import { V3, generate2QFromState, apply2QNoise } from "../math";
import type { ProbeStateConfig, TopologyConfig } from "../types";

interface TwoQubitSceneProps {
  topoConfigs: Record<string, TopologyConfig>;
  activeTopo: string; // key or "all"
  strength: number;
  rotation: number;
  stateCfg: ProbeStateConfig;
}

export default function TwoQubitScene({
  topoConfigs,
  activeTopo,
  strength,
  rotation,
  stateCfg,
}: TwoQubitSceneProps) {
  const mountRef = useRef<HTMLDivElement>(null);
  const frameRef = useRef<number>(0);

  const pRef = useRef({ rotation, activeTopo, strength });
  useEffect(() => { pRef.current = { rotation, activeTopo, strength }; });
  const topoRef = useRef(topoConfigs);
  useEffect(() => { topoRef.current = topoConfigs; }, [topoConfigs]);

  const basePts = useMemo(() => generate2QFromState(stateCfg, 450), [stateCfg]);
  const basePtsRef = useRef(basePts);
  useEffect(() => { basePtsRef.current = basePts; }, [basePts]);

  const key = `2q-${stateCfg?.name}-${JSON.stringify(stateCfg?.correlators)}`;

  useEffect(() => {
    const el = mountRef.current;
    if (!el) return;
    const w = el.clientWidth, h = el.clientHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(chrome.bg.primary);
    const camera = new THREE.PerspectiveCamera(40, w / h, 0.1, 100);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    el.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0x404060, 0.8));
    const dl = new THREE.DirectionalLight(0xffffff, 0.6);
    dl.position.set(3, 4, 2);
    scene.add(dl);

    // Axes: ZI, IZ, ZZ
    const axC = [0xff4466, 0x44ff88, 0x4488ff];
    [V3(1, 0, 0), V3(0, 1, 0), V3(0, 0, 1)].forEach((d, i) => {
      scene.add(new THREE.Line(
        new THREE.BufferGeometry().setFromPoints([d.clone().multiplyScalar(-1.4), d.clone().multiplyScalar(1.4)]),
        new THREE.LineBasicMaterial({ color: axC[i], transparent: true, opacity: 0.4 }),
      ));
    });

    const pts = basePtsRef.current;

    const mkCloud = (color: number, size: number, opacity: number): THREE.Points => {
      const g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pts.length * 3), 3));
      const c = new THREE.Points(g, new THREE.PointsMaterial({ color, size, transparent: true, opacity }));
      scene.add(c);
      return c;
    };

    // Original cloud
    const origCloud = mkCloud(0x3366aa, 0.016, 0.25);
    const op = origCloud.geometry.attributes.position.array as Float32Array;
    pts.forEach((p, i) => {
      op[i * 3] = p.zi;
      op[i * 3 + 1] = p.zz;
      op[i * 3 + 2] = p.iz;
    });
    origCloud.geometry.attributes.position.needsUpdate = true;

    // Topology clouds with distinct colors
    const topoColors = [0xff9933, 0xcc44ff, 0x44ddff, 0xff4466, 0x44ff88];
    const topoClouds: Record<string, THREE.Points> = {};
    Object.keys(topoConfigs).forEach((k, i) => {
      topoClouds[k] = mkCloud(topoColors[i % topoColors.length], 0.022, 0.6);
    });

    const animate = () => {
      frameRef.current = requestAnimationFrame(animate);
      const pr = pRef.current;
      camera.position.set(
        3.0 * Math.cos(pr.rotation),
        1.6,
        3.0 * Math.sin(pr.rotation),
      );
      camera.lookAt(0, 0, 0);

      const topos = topoRef.current;
      const curPts = basePtsRef.current;
      for (const [k, cloud] of Object.entries(topoClouds)) {
        const show = pr.activeTopo === "all" || pr.activeTopo === k;
        cloud.visible = show;
        if (show && topos[k] && curPts) {
          const noised = apply2QNoise(curPts, topos[k], pr.strength);
          const pos = cloud.geometry.attributes.position.array as Float32Array;
          noised.forEach((pt, i) => {
            pos[i * 3] = pt.zi;
            pos[i * 3 + 1] = pt.zz;
            pos[i * 3 + 2] = pt.iz;
          });
          cloud.geometry.attributes.position.needsUpdate = true;
        }
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
    <div
      ref={mountRef}
      style={{ width: "100%", height: "100%", borderRadius: "8px", overflow: "hidden" }}
    />
  );
}
