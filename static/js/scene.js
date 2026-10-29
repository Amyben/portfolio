// Scène 3D de l'en-tête : un réseau en orbite autour d'un cœur « pare-feu ».
// Cœur (icosaèdre filaire) → commutateurs sur un anneau → postes en périphérie,
// avec des impulsions lumineuses qui circulent sur les liaisons.
// Repli : si WebGL ou le CDN manquent, l'image SVG du conteneur reste affichée.
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

const host = document.querySelector("[data-scene]");
if (host) {
  try {
    start(host);
  } catch (err) {
    console.warn("Scène 3D désactivée :", err);
  }
}

function start(host) {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const small = window.matchMedia("(max-width: 860px)").matches;

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "low-power" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  host.appendChild(renderer.domElement);
  host.classList.add("is-live");

  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x090d1f, 0.055);
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(0, 0.6, 11);

  const COLORS = { glow: 0x7fe0ff, ion: 0x4f8dff, soft: 0x8fb4ff, white: 0xdff6ff };
  const world = new THREE.Group();
  scene.add(world);

  // Texture ronde et douce pour les points lumineux.
  const dot = (() => {
    const c = document.createElement("canvas");
    c.width = c.height = 64;
    const g = c.getContext("2d");
    const grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    grd.addColorStop(0, "rgba(255,255,255,1)");
    grd.addColorStop(0.25, "rgba(200,240,255,.85)");
    grd.addColorStop(1, "rgba(120,190,255,0)");
    g.fillStyle = grd;
    g.fillRect(0, 0, 64, 64);
    return new THREE.CanvasTexture(c);
  })();
  const glowMaterial = (color, size, opacity = 1) =>
    new THREE.PointsMaterial({ color, size, map: dot, transparent: true, opacity, depthWrite: false, blending: THREE.AdditiveBlending });

  // --- Cœur : icosaèdre filaire + noyau lumineux ---
  const core = new THREE.Group();
  const ico = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(1.05, 1)),
    new THREE.LineBasicMaterial({ color: COLORS.glow, transparent: true, opacity: 0.85 })
  );
  const shell = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.IcosahedronGeometry(1.45, 0)),
    new THREE.LineBasicMaterial({ color: COLORS.ion, transparent: true, opacity: 0.35 })
  );
  const nucleus = new THREE.Points(new THREE.BufferGeometry().setAttribute("position", new THREE.Float32BufferAttribute([0, 0, 0], 3)), glowMaterial(COLORS.glow, 3.2, 0.9));
  core.add(ico, shell, nucleus);
  world.add(core);

  // --- Orbites ---
  const orbit = (radius, tiltX, tiltZ, opacity) => {
    const pts = new THREE.EllipseCurve(0, 0, radius, radius).getPoints(160).map((p) => new THREE.Vector3(p.x, 0, p.y));
    const line = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: COLORS.soft, transparent: true, opacity }));
    line.rotation.set(tiltX, 0, tiltZ);
    world.add(line);
    return line;
  };
  orbit(2.6, 0.35, 0.1, 0.28);
  orbit(4.1, -0.25, -0.18, 0.16);
  orbit(5.6, 0.12, 0.3, 0.08);

  // --- Commutateurs sur l'anneau intérieur ---
  const rand = mulberry32(7);
  const ring = new THREE.Object3D();
  ring.rotation.set(0.35, 0, 0.1);
  world.add(ring);
  const SWITCHES = 6;
  const switches = [];
  for (let i = 0; i < SWITCHES; i++) {
    const a = (i / SWITCHES) * Math.PI * 2;
    const p = new THREE.Vector3(Math.cos(a) * 2.6, 0, Math.sin(a) * 2.6);
    const box = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.14, 0.24), new THREE.MeshBasicMaterial({ color: 0x0f1a44 }));
    const edges = new THREE.LineSegments(new THREE.EdgesGeometry(box.geometry), new THREE.LineBasicMaterial({ color: COLORS.glow }));
    box.add(edges);
    box.position.copy(p);
    box.lookAt(0, 0, 0);
    ring.add(box);
    switches.push(box);
  }

  // --- Postes en périphérie, rattachés au commutateur le plus proche ---
  const HOSTS = small ? 22 : 40;
  const hostPositions = [];
  const links = []; // [départ, arrivée] en coordonnées du monde
  ring.updateMatrixWorld(true);
  const switchWorld = switches.map((s) => s.getWorldPosition(new THREE.Vector3()));
  for (let i = 0; i < HOSTS; i++) {
    const r = 3.6 + rand() * 2.4;
    const theta = rand() * Math.PI * 2;
    const phi = Math.acos(2 * rand() - 1) * 0.55 + Math.PI * 0.225; // concentrés près de l'équateur
    const p = new THREE.Vector3(r * Math.sin(phi) * Math.cos(theta), r * Math.cos(phi), r * Math.sin(phi) * Math.sin(theta));
    hostPositions.push(p);
    let best = switchWorld[0];
    for (const s of switchWorld) if (s.distanceTo(p) < best.distanceTo(p)) best = s;
    links.push([best, p]);
  }
  for (const s of switchWorld) links.push([new THREE.Vector3(), s]);
  for (let i = 0; i < SWITCHES; i++) links.push([switchWorld[i], switchWorld[(i + 1) % SWITCHES]]);

  world.add(new THREE.Points(new THREE.BufferGeometry().setFromPoints(hostPositions), glowMaterial(COLORS.soft, 0.32, 0.95)));

  // Liaisons légèrement courbées (vers le centre) pour la profondeur.
  const curves = links.map(([a, b]) => {
    const mid = a.clone().add(b).multiplyScalar(0.5);
    mid.multiplyScalar(0.86).add(new THREE.Vector3(0, 0.25, 0));
    return new THREE.QuadraticBezierCurve3(a, mid, b);
  });
  const linkVerts = [];
  for (const c of curves) {
    const pts = c.getPoints(20);
    for (let i = 0; i < pts.length - 1; i++) linkVerts.push(pts[i], pts[i + 1]);
  }
  world.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(linkVerts), new THREE.LineBasicMaterial({ color: COLORS.ion, transparent: true, opacity: 0.32, blending: THREE.AdditiveBlending, depthWrite: false })));

  // --- Impulsions qui voyagent sur les liaisons ---
  const PULSES = small ? 14 : 26;
  const pulses = Array.from({ length: PULSES }, () => ({ curve: curves[Math.floor(rand() * curves.length)], t: rand(), speed: 0.12 + rand() * 0.22 }));
  const pulseGeo = new THREE.BufferGeometry();
  const pulseArr = new Float32Array(PULSES * 3);
  pulseGeo.setAttribute("position", new THREE.BufferAttribute(pulseArr, 3));
  world.add(new THREE.Points(pulseGeo, glowMaterial(COLORS.white, 0.42)));

  // --- Champ d'étoiles lointain ---
  const stars = [];
  for (let i = 0; i < 700; i++) {
    const v = new THREE.Vector3(rand() - 0.5, rand() - 0.5, rand() - 0.5).normalize().multiplyScalar(18 + rand() * 20);
    stars.push(v);
  }
  const starField = new THREE.Points(new THREE.BufferGeometry().setFromPoints(stars), new THREE.PointsMaterial({ color: 0x9fb8ff, size: 0.07, transparent: true, opacity: 0.6, depthWrite: false }));
  scene.add(starField);

  // --- Mise en page : la scène se place à droite sur grand écran, en haut sur mobile ---
  function layout() {
    const w = host.clientWidth, h = host.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    const wide = w > 860;
    world.position.set(wide ? Math.min(4.2, 1.2 + (w / h) * 1.35) : 0, wide ? 0 : 2.2, 0);
    world.scale.setScalar(wide ? 1 : 0.78);
  }
  new ResizeObserver(layout).observe(host);
  layout();

  // --- Interaction : la scène suit doucement le pointeur ---
  const target = { x: 0, y: 0 };
  window.addEventListener("pointermove", (e) => {
    target.x = (e.clientX / window.innerWidth - 0.5) * 0.5;
    target.y = (e.clientY / window.innerHeight - 0.5) * 0.3;
  }, { passive: true });

  // --- Boucle : pause hors écran ou onglet masqué ---
  let visible = true;
  new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; if (visible) loop(); }).observe(host);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) loop(); });

  const clock = new THREE.Clock();
  let running = false;
  function frame() {
    const dt = Math.min(clock.getDelta(), 0.05);
    const t = clock.elapsedTime;
    world.rotation.y += dt * 0.08;
    world.rotation.x += (target.y - world.rotation.x) * 0.04;
    world.rotation.z += (-target.x * 0.3 - world.rotation.z) * 0.04;
    ico.rotation.x += dt * 0.25;
    ico.rotation.y -= dt * 0.18;
    shell.rotation.y += dt * 0.1;
    nucleus.material.size = 3.2 + Math.sin(t * 2.2) * 0.5;
    starField.rotation.y -= dt * 0.005;
    pulses.forEach((p, i) => {
      p.t += dt * p.speed;
      if (p.t > 1) { p.t = 0; p.curve = curves[Math.floor(rand() * curves.length)]; }
      const v = p.curve.getPoint(p.t);
      pulseArr.set([v.x, v.y, v.z], i * 3);
    });
    pulseGeo.attributes.position.needsUpdate = true;
    renderer.render(scene, camera);
  }
  function loop() {
    if (running || reduceMotion) return;
    running = true;
    clock.getDelta();
    const tick = () => {
      if (!visible || document.hidden) { running = false; return; }
      frame();
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  if (reduceMotion) {
    // Une seule image fixe, recalculée au redimensionnement.
    pulses.forEach((p, i) => { const v = p.curve.getPoint(p.t); pulseArr.set([v.x, v.y, v.z], i * 3); });
    world.rotation.set(0.12, -0.5, 0);
    const still = () => renderer.render(scene, camera);
    new ResizeObserver(still).observe(host);
    still();
  } else {
    loop();
  }
}

// Générateur pseudo-aléatoire déterministe : la constellation est identique à chaque visite.
function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
