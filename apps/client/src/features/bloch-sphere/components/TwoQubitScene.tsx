'use dom';

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { V3, generate2QFromState, apply2QNoise } from "../math";
import type {
  ProbeStateConfig,
  TopologyConfig,
} from "../types";

interface TwoQubitSceneProps {
  state: ProbeStateConfig;
  topology: TopologyConfig;
  errorRate: number;
}

export default function TwoQubitScene({
  state,
  topology,
  errorRate,
}: TwoQubitSceneProps) {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<{
    renderer: THREE.WebGLRenderer;
    scene: THREE.Scene;
    camera: THREE.PerspectiveCamera;
    cleanCloud: THREE.Points;
    noisyCloud: THREE.Points;
    frameId: number;
  } | null>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const w = mount.clientWidth;
    const h = mount.clientHeight;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(window.devicePixelRatio);
    mount.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100);
    camera.position.set(2.5, 1.8, 2.5);
    camera.lookAt(0, 0, 0);

    // Axes for correlator space: ZI, IZ, ZZ
    const axisColors = [0xff4444, 0x44ff44, 0x4488ff];
    const axisDirs = [V3(1, 0, 0), V3(0, 1, 0), V3(0, 0, 1)];
    axisDirs.forEach((dir, i) => {
      const arrow = new THREE.ArrowHelper(
        dir,
        V3(0, 0, 0),
        1.3,
        axisColors[i],
        0.08,
        0.05,
      );
      scene.add(arrow);
      const negArrow = new THREE.ArrowHelper(
        dir.clone().negate(),
        V3(0, 0, 0),
        1.3,
        axisColors[i],
        0.08,
        0.05,
      );
      scene.add(negArrow);
    });

    // Grid plane
    const grid = new THREE.GridHelper(2, 10, 0x222244, 0x111133);
    scene.add(grid);

    const N = 400;
    const makeCloud = (color: number, size: number): THREE.Points => {
      const geo = new THREE.BufferGeometry();
      geo.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(new Float32Array(N * 3), 3),
      );
      const mat = new THREE.PointsMaterial({
        color,
        size,
        transparent: true,
        opacity: 0.6,
        sizeAttenuation: true,
      });
      const pts = new THREE.Points(geo, mat);
      scene.add(pts);
      return pts;
    };

    const cleanCloud = makeCloud(0x44ddff, 0.03);
    const noisyCloud = makeCloud(0xff6644, 0.03);

    let frameId = 0;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      const t = Date.now() * 0.0002;
      scene.rotation.y = t;
      renderer.render(scene, camera);
    };
    animate();

    sceneRef.current = {
      renderer,
      scene,
      camera,
      cleanCloud,
      noisyCloud,
      frameId,
    };

    const handleResize = () => {
      if (!mount) return;
      const nw = mount.clientWidth;
      const nh = mount.clientHeight;
      camera.aspect = nw / nh;
      camera.updateProjectionMatrix();
      renderer.setSize(nw, nh);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(frameId);
      renderer.dispose();
      if (mount.contains(renderer.domElement)) {
        mount.removeChild(renderer.domElement);
      }
    };
  }, []);

  // Update points
  useEffect(() => {
    const s = sceneRef.current;
    if (!s) return;
    const N = 400;

    const cleanSamples = generate2QFromState(state, N);
    const cleanPos = s.cleanCloud.geometry.attributes
      .position as THREE.BufferAttribute;
    for (let i = 0; i < N; i++) {
      const pt = cleanSamples[i];
      cleanPos.setXYZ(i, pt.zi, pt.iz, pt.zz);
    }
    cleanPos.needsUpdate = true;

    const noisyPos = s.noisyCloud.geometry.attributes
      .position as THREE.BufferAttribute;
    if (errorRate > 0) {
      const noised = apply2QNoise(cleanSamples, topology, errorRate);
      for (let i = 0; i < N; i++) {
        const pt = noised[i];
        noisyPos.setXYZ(i, pt.zi, pt.iz, pt.zz);
      }
      (s.noisyCloud.material as THREE.PointsMaterial).opacity = 0.5;
    } else {
      for (let i = 0; i < N; i++) {
        noisyPos.setXYZ(i, 0, 0, 0);
      }
      (s.noisyCloud.material as THREE.PointsMaterial).opacity = 0;
    }
    noisyPos.needsUpdate = true;
  }, [state, topology, errorRate]);

  return (
    <div
      ref={mountRef}
      style={{
        width: "100%",
        height: "100%",
        minHeight: 250,
        borderRadius: 8,
        overflow: "hidden",
      }}
    />
  );
}
