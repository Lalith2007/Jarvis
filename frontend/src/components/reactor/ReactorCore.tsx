import { Float, Sparkles } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { Bloom, EffectComposer } from "@react-three/postprocessing";
import { useMemo, useRef } from "react";
import * as THREE from "three";
import { useJarvisStore } from "../../stores/use-jarvis-store";
import type { ReactorMode } from "../../types/jarvis";

const modeConfig: Record<ReactorMode, { speed: number; intensity: number; color: string; particles: number }> = {
  offline: { speed: .035, intensity: .42, color: "#23576b", particles: 24 },
  idle: { speed: .12, intensity: 1.2, color: "#00c8ff", particles: 70 },
  listening: { speed: .3, intensity: 2.2, color: "#38e8ff", particles: 110 },
  thinking: { speed: .72, intensity: 2.8, color: "#168cff", particles: 150 },
  routing: { speed: .6, intensity: 2.5, color: "#7d00ff", particles: 140 },
  collaborating: { speed: .55, intensity: 3, color: "#7f8cff", particles: 180 },
  browsing: { speed: .42, intensity: 2.4, color: "#00e5ff", particles: 120 },
  memory: { speed: .32, intensity: 2.3, color: "#8d7dff", particles: 130 },
  coding: { speed: .5, intensity: 2.6, color: "#14d9ff", particles: 140 },
  speaking: { speed: .25, intensity: 3.2, color: "#5cf2ff", particles: 160 },
  error: { speed: .8, intensity: 3.4, color: "#ff3b68", particles: 170 },
};

function SegmentRing({ radius, segments, rotation = 0, color, opacity = .8 }: { radius: number; segments: number; rotation?: number; color: string; opacity?: number }) {
  const group = useRef<THREE.Group>(null);
  return (
    <group ref={group} rotation={[0, 0, rotation]}>
      {Array.from({ length: segments }, (_, index) => {
        const length = index % 4 === 0 ? .14 : .065;
        const angle = (index / segments) * Math.PI * 2;
        return (
          <mesh key={index} position={[Math.cos(angle) * radius, Math.sin(angle) * radius, 0]} rotation={[0, 0, angle]}>
            <boxGeometry args={[length, index % 5 === 0 ? .015 : .006, .01]} />
            <meshBasicMaterial color={color} transparent opacity={opacity * (index % 3 === 0 ? 1 : .48)} toneMapped={false} />
          </mesh>
        );
      })}
    </group>
  );
}

function EnergyRay({ angle, length, color, opacity = .5 }: { angle: number; length: number; color: string; opacity?: number }) {
  return (
    <mesh rotation={[0, 0, angle]} position={[Math.cos(angle) * length / 2, Math.sin(angle) * length / 2, -.02]}>
      <boxGeometry args={[length, .006, .006]} />
      <meshBasicMaterial color={color} transparent opacity={opacity} toneMapped={false} />
    </mesh>
  );
}

function ReactorScene({ mode, sector }: { mode: ReactorMode; sector: string | null }) {
  const outer = useRef<THREE.Group>(null);
  const middle = useRef<THREE.Group>(null);
  const inner = useRef<THREE.Group>(null);
  const pulse = useRef<THREE.Mesh>(null);
  const config = modeConfig[mode];
  const sectorAngle = sector ? (Array.from(sector).reduce((sum, char) => sum + char.charCodeAt(0), 0) % 360) * Math.PI / 180 : 0;

  useFrame(({ clock, pointer }) => {
    const t = clock.getElapsedTime();
    if (outer.current) { outer.current.rotation.z = t * config.speed * .24; outer.current.rotation.x = pointer.y * .045; outer.current.rotation.y = pointer.x * .045; }
    if (middle.current) middle.current.rotation.z = -t * config.speed * .52;
    if (inner.current) inner.current.rotation.z = t * config.speed * .9;
    if (pulse.current) {
      const voicePulse = mode === "speaking" ? Math.sin(t * 9) * .11 : Math.sin(t * 2.2) * .035;
      pulse.current.scale.setScalar(1 + voicePulse);
    }
  });

  const rays = useMemo(() => [0, .5, 1.4, 2.25, 3.15, 4.1, 5.12], []);
  return (
    <>
    <Float speed={.7} rotationIntensity={.03} floatIntensity={.08}>
      <group rotation={[-.03, 0, 0]}>
        <group ref={outer}>
          <mesh><torusGeometry args={[2.25, .008, 8, 160]} /><meshBasicMaterial color={config.color} transparent opacity={.28} toneMapped={false} /></mesh>
          <mesh rotation={[0, 0, .06]}><torusGeometry args={[2.08, .018, 8, 120, Math.PI * 1.62]} /><meshBasicMaterial color={config.color} transparent opacity={.66} toneMapped={false} /></mesh>
          <SegmentRing radius={2.38} segments={96} color={config.color} opacity={.55} />
          <SegmentRing radius={1.9} segments={72} rotation={.18} color={config.color} opacity={.9} />
        </group>
        <group ref={middle}>
          <mesh><torusGeometry args={[1.55, .026, 8, 140, Math.PI * 1.78]} /><meshBasicMaterial color={config.color} transparent opacity={.88} toneMapped={false} /></mesh>
          <mesh rotation={[0, 0, 2.2]}><torusGeometry args={[1.34, .009, 8, 120, Math.PI * 1.2]} /><meshBasicMaterial color="#6deaff" transparent opacity={.75} toneMapped={false} /></mesh>
          <SegmentRing radius={1.72} segments={64} color={config.color} opacity={.75} />
          {rays.map((angle, index) => <EnergyRay key={angle} angle={angle} length={index % 2 ? 1.8 : 2.25} color={config.color} opacity={index % 2 ? .25 : .6} />)}
        </group>
        <group ref={inner}>
          <mesh><torusGeometry args={[.84, .032, 10, 100]} /><meshBasicMaterial color="#5beaff" transparent opacity={.9} toneMapped={false} /></mesh>
          <mesh><torusGeometry args={[.62, .012, 8, 80]} /><meshBasicMaterial color={config.color} transparent opacity={.82} toneMapped={false} /></mesh>
          <SegmentRing radius={1.05} segments={40} color="#a2f5ff" opacity={.95} />
        </group>
        <mesh ref={pulse}>
          <circleGeometry args={[.42, 64]} />
          <meshBasicMaterial color={config.color} transparent opacity={.16} blending={THREE.AdditiveBlending} toneMapped={false} />
        </mesh>
        <mesh position={[0, 0, .04]}>
          <sphereGeometry args={[.10, 24, 24]} />
          <meshBasicMaterial color="#d8fbff" toneMapped={false} />
        </mesh>
        <mesh position={[0, 0, .02]}>
          <ringGeometry args={[.14, .22, 48]} />
          <meshBasicMaterial color={config.color} transparent opacity={.95} toneMapped={false} />
        </mesh>
        {sector && (
          <group rotation={[0, 0, sectorAngle]}>
            <mesh rotation={[0, 0, Math.PI / 2]} position={[1.55, 0, .08]}>
              <planeGeometry args={[.12, 1.15]} />
              <meshBasicMaterial color="#d7fbff" transparent opacity={.7} blending={THREE.AdditiveBlending} toneMapped={false} />
            </mesh>
          </group>
        )}
        <Sparkles key={config.particles} count={config.particles} scale={5.2} size={1.8} speed={config.speed * .45} color={config.color} opacity={.75} />
      </group>
    </Float>
    <EffectComposer multisampling={0}>
      <Bloom intensity={config.intensity} luminanceThreshold={.08} luminanceSmoothing={.8} mipmapBlur />
    </EffectComposer>
    </>
  );
}

export function ReactorCore({ compact = false }: { compact?: boolean }) {
  const mode = useJarvisStore((state) => state.reactorMode);
  const sector = useJarvisStore((state) => state.activeSector);
  return (
    <div className={`reactor-wrap mode-${mode}${compact ? " compact" : ""}`} aria-label={`JARVIS reactor: ${mode}`}>
      <div className="reactor-grid" />
      <div className="reactor-scanline" />
      <Canvas
        dpr={[1, 1.5]}
        camera={{ position: [0, 0, 5.8], fov: 50 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ReactorScene mode={mode} sector={sector} />
      </Canvas>
      <div className="reactor-reticle"><i /><i /><i /><i /></div>
    </div>
  );
}
