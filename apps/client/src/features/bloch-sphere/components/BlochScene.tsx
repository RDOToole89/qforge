'use dom';

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { V3, TAU, spherePoints, statePoints } from "../math";
import type { ProbeStateConfig, RuntimeChannel } from "../types";

interface BlochSceneProps {
  state: ProbeStateConfig;
  channel: RuntimeChannel | null;
  errorRate: number;
  pointCount: number;
}

export default function BlochScene({
  state,
  channel,
  errorRate,
  pointCount,
}: BlochSceneProps) {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<{
    renderer: THREE.WebGLRenderer;
    scene: THREE.Scene;
    camera: THREE.PerspectiveCamera;
    cleanCloud: THREE.Points;
    noisyCloud: THREE.Points;
    frameId: number;
  } | null>(null);

  // Initialize Three.js scene
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
    camera.position.set(2.2, 1.5, 2.2);
    camera.lookAt(0, 0, 0);

    // Wireframe sphere
    const wireGeo = new THREE.SphereGeometry(1, 24, 16);
    const wireMat = new THREE.MeshBasicMaterial({
      color: 0x334455,
      wireframe: true,
      transparent: true,
      opacity: 0.15,
    });
    scene.add(new THREE.Mesh(wireGeo, wireMat));

    // Axes
    const axisColors = [0xff4444, 0x44ff44, 0x4488ff];
    const axisLabels = ["X", "Y", "Z"];
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
    });

    // Point clouds
    const makeCloud = (color: number, size: number): THREE.Points => {
      const geo = new THREE.BufferGeometry();
      geo.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(new Float32Array(pointCount * 3), 3),
      );
      const mat = new THREE.PointsMaterial({
        color,
        size,
        transparent: true,
        opacity: 0.7,
        sizeAttenuation: true,
      });
      const pts = new THREE.Points(geo, mat);
      scene.add(pts);
      return pts;
    };

    const cleanCloud = makeCloud(0x44ddff, 0.025);
    const noisyCloud = makeCloud(0xff6644, 0.025);

    let frameId = 0;
    const animate = () => {
      frameId = requestAnimationFrame(animate);
      const t = Date.now() * 0.0003;
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
  }, [pointCount]);

  // Update point clouds when state/channel/error changes
  useEffect(() => {
    const s = sceneRef.current;
    if (!s) return;

    const cleanPts = statePoints(state, pointCount);
    const cleanPos = s.cleanCloud.geometry.attributes
      .position as THREE.BufferAttribute;
    for (let i = 0; i < pointCount; i++) {
      const pt = cleanPts[i] ?? V3(0, 0, 0);
      cleanPos.setXYZ(i, pt.x, pt.y, pt.z);
    }
    cleanPos.needsUpdate = true;

    // Noisy cloud
    const noisyPos = s.noisyCloud.geometry.attributes
      .position as THREE.BufferAttribute;
    if (channel && errorRate > 0) {
      const spherePts = spherePoints(pointCount);
      for (let i = 0; i < pointCount; i++) {
        const pt = channel.apply(
          { x: spherePts[i].x, y: spherePts[i].y, z: spherePts[i].z },
          errorRate,
        );
        noisyPos.setXYZ(i, pt.x, pt.y, pt.z);
      }
      (s.noisyCloud.material as THREE.PointsMaterial).opacity = 0.5;
    } else {
      for (let i = 0; i < pointCount; i++) {
        noisyPos.setXYZ(i, 0, 0, 0);
      }
      (s.noisyCloud.material as THREE.PointsMaterial).opacity = 0;
    }
    noisyPos.needsUpdate = true;
  }, [state, channel, errorRate, pointCount]);

  return (
    <div
      ref={mountRef}
      style={{
        width: "100%",
        height: "100%",
        minHeight: 300,
        borderRadius: 8,
        overflow: "hidden",
      }}
    />
  );
}
