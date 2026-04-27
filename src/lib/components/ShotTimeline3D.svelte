<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls, GLTFLoader } from 'three-stdlib';

  import ballModelUrl from '$lib/assets/basketball.glb?url';
  import courtModelUrl from '$lib/assets/houston_rockets_basketball_stadium.glb?url';
  import type { HeatmapCell, HeatmapPayload, ShotOutcome } from '$lib/types';

  export let heatmap: HeatmapPayload | null = null;
  export let seasons: string[] = [];
  export let selectedSeason = 'all';
  export let shotOutcome: ShotOutcome = 'made';
  export let profileMode: 'league' | 'player' = 'league';
  export let playerTargetDistance: number | null = null;
  export let speed = 1;
  export let playing = true;
  export let loopSeasons = true;
  export let showControls = true;

  const hoopDataY = 4;
  const hoopWorldY = 10;
  const dataHalfCourtLength = 47;
  type OrbitControlsInstance = InstanceType<typeof OrbitControls>;

  let host: HTMLDivElement;
  let renderer: THREE.WebGLRenderer | null = null;
  let camera: THREE.PerspectiveCamera | null = null;
  let scene: THREE.Scene | null = null;
  let controls: OrbitControlsInstance | null = null;
  let resizeObserver: ResizeObserver | null = null;

  let animationFrame = 0;
  let seasonTimer: ReturnType<typeof setInterval> | null = null;
  let spawnTimer: ReturnType<typeof setInterval> | null = null;

  let activeSeasonIndex = 0;
  let activeSeason = '';
  let previousActiveSeason = '';
  let currentBins: WeightedBin[] = [];

  let courtRoot: THREE.Object3D | null = null;
  let ballTemplate: THREE.Object3D | null = null;
  let hoopAnchor: THREE.Vector3 | null = null;
  let oppositeHoopAnchor: THREE.Vector3 | null = null;
  let stadiumBounds: THREE.Box3 | null = null;
  let assetsReady = false;

  let courtMinX = -25;
  let courtMaxX = 25;
  let courtStartZ = 0;
  let courtEndZ = dataHalfCourtLength;
  let courtFloorY = 0;
  let unitsPerFootX = 1;
  let unitsPerFootZ = 1;
  let zDirectionFromHoop = 1;
  let shotOffsetX = 0;
  let shotOffsetZ = 0;

  let tuneOffsetX = -0.5;
  let tuneOffsetZ = -18.1;
  let tuneScaleX = 0.43;
  let tuneScaleZ = 0.66;
  let tuneFloorOffset = 7.55;
  let tuneRimHeightOffset = -6;
  let tuneReleaseHeight = -9.1;
  let tuneArcHeight = -20;
  let tuneBallScale = 0.6;

  const loader = new GLTFLoader();

  const originRingGeometry = new THREE.RingGeometry(0.34, 0.56, 32);
  const originMadeMaterial = new THREE.MeshBasicMaterial({
    color: 0x14b8a6,
    transparent: true,
    opacity: 0.95,
    side: THREE.DoubleSide,
    depthTest: false,
    depthWrite: false
  });
  const originMissMaterial = new THREE.MeshBasicMaterial({
    color: 0xf97316,
    transparent: true,
    opacity: 0.95,
    side: THREE.DoubleSide,
    depthTest: false,
    depthWrite: false
  });

  interface Vec3 {
    x: number;
    y: number;
    z: number;
  }

  interface WeightedBin {
    x: number;
    y: number;
    distance: number;
    baseWeight: number;
  }

  interface ShotPoolBin extends WeightedBin {
    remaining: number;
  }

  interface AnimatedShot {
    start: Vec3;
    control: Vec3;
    end: Vec3;
    startedAt: number;
    durationMs: number;
    made: boolean;
    ballMesh: THREE.Object3D;
    originMarker: THREE.Mesh;
    connectorLine: THREE.Line;
  }

  let shots: AnimatedShot[] = [];
  let shotPool: ShotPoolBin[] = [];
  let shotPoolRemaining = 0;
  let pausedAtMs: number | null = null;
  const shotVerticalNudge = -0.75;
  const baseBurstSize = 5;

  $: timelineSeasons =
    selectedSeason === 'all'
      ? seasons
      : seasons.includes(selectedSeason)
        ? [selectedSeason]
        : seasons.length
          ? [seasons[0]]
          : [];

  $: if (!timelineSeasons.length) {
    activeSeasonIndex = 0;
    activeSeason = '';
  } else if (selectedSeason !== 'all') {
    activeSeasonIndex = 0;
    activeSeason = timelineSeasons[0];
  } else {
    activeSeasonIndex = Math.min(activeSeasonIndex, timelineSeasons.length - 1);
    activeSeason = timelineSeasons[activeSeasonIndex];
  }

  $: currentBins = buildWeightedBins(
    heatmap?.bySeason?.[activeSeason] ?? [],
    shotOutcome,
    profileMode,
    playerTargetDistance
  );
  $: {
    currentBins;
    activeSeason;
    refillShotPool();
  }

  $: if (activeSeason !== previousActiveSeason) {
    previousActiveSeason = activeSeason;
    clearShots();
    refillShotPool();
  }

  $: {
    playing;
    loopSeasons;
    selectedSeason;
    timelineSeasons;
    currentBins;
    assetsReady;
    speed;

    if (!playing) {
      stopTimers();
    } else {
      restartSeasonTimer();
      restartSpawnTimer();
    }
  }

  $: if (!playing && pausedAtMs === null) {
    pausedAtMs = nowMs();
  }

  $: if (playing && pausedAtMs !== null) {
    const elapsedWhilePaused = nowMs() - pausedAtMs;
    for (const shot of shots) {
      shot.startedAt += elapsedWhilePaused;
    }
    pausedAtMs = null;
  }

  function nowMs() {
    return typeof performance !== 'undefined' ? performance.now() : Date.now();
  }

  function stopTimers() {
    if (seasonTimer) {
      clearInterval(seasonTimer);
      seasonTimer = null;
    }

    if (spawnTimer) {
      clearInterval(spawnTimer);
      spawnTimer = null;
    }
  }

  function dataToWorld(x: number, y: number): Vec3 {
    const clampedXFeet = clamp(x, -25, 25);
    const clampedYFeet = clamp(y, 0, 47);
    const worldX = shotOffsetX + tuneOffsetX + clampedXFeet * unitsPerFootX * tuneScaleX;
    const worldZ =
      shotOffsetZ +
      tuneOffsetZ +
      (clampedYFeet - hoopDataY) * unitsPerFootZ * tuneScaleZ * zDirectionFromHoop;

    return {
      x: worldX,
      y: courtFloorY + tuneFloorOffset,
      z: worldZ
    };
  }

  function effectiveRimHeight() {
    return hoopWorldY + tuneRimHeightOffset;
  }

  function centerCourtPoint() {
    if (stadiumBounds) {
      const center = stadiumBounds.getCenter(new THREE.Vector3());
      return {
        x: center.x,
        z: center.z
      };
    }

    if (hoopAnchor && oppositeHoopAnchor) {
      return {
        x: (hoopAnchor.x + oppositeHoopAnchor.x) / 2,
        z: (hoopAnchor.z + oppositeHoopAnchor.z) / 2
      };
    }
    return {
      x: shotOffsetX,
      z: shotOffsetZ + 43
    };
  }

  function focusCourtPoint() {
    if (hoopAnchor && oppositeHoopAnchor) {
      return {
        x: hoopAnchor.x * 0.78 + oppositeHoopAnchor.x * 0.22,
        z: hoopAnchor.z * 0.78 + oppositeHoopAnchor.z * 0.22
      };
    }

    const center = centerCourtPoint();
    return {
      x: center.x,
      z: center.z - 10
    };
  }

  function configureCenterCourtCamera(resetPosition = false) {
    if (!camera || !controls) return;

    const focus = focusCourtPoint();
    const boundsSize = stadiumBounds?.getSize(new THREE.Vector3());
    const cameraHeight = courtFloorY + 14;
    const sidelineOffset = boundsSize ? Math.min(15, Math.max(7, boundsSize.x * 0.16)) : 10;
    const baselineOffset = boundsSize ? Math.min(22, Math.max(10, boundsSize.z * 0.14)) : 14;

    controls.target.set(focus.x, courtFloorY + 7, focus.z);
    controls.enablePan = true;
    controls.minDistance = 6;
    controls.maxDistance = boundsSize ? Math.max(24, Math.min(boundsSize.x, boundsSize.z) * 0.45) : 90;
    controls.maxPolarAngle = THREE.MathUtils.degToRad(86);

    if (resetPosition) {
      camera.position.set(focus.x + sidelineOffset, cameraHeight, focus.z + baselineOffset);
    }

    controls.update();
    clampCameraInsideStadium();
  }

  function clampCameraInsideStadium() {
    if (!camera || !stadiumBounds) return;

    const margin = 4;
    camera.position.x = clamp(camera.position.x, stadiumBounds.min.x + margin, stadiumBounds.max.x - margin);
    camera.position.y = clamp(camera.position.y, stadiumBounds.min.y + margin, stadiumBounds.max.y - margin);
    camera.position.z = clamp(camera.position.z, stadiumBounds.min.z + margin, stadiumBounds.max.z - margin);
  }

  function orientCourtModel(object: THREE.Object3D) {
    const initialBox = new THREE.Box3().setFromObject(object);
    const initialSize = initialBox.getSize(new THREE.Vector3());
    const verticalAxis = ['x', 'y', 'z'].reduce((minAxis, axis) =>
      initialSize[axis as 'x' | 'y' | 'z'] < initialSize[minAxis as 'x' | 'y' | 'z'] ? axis : minAxis
    , 'y');

    if (verticalAxis === 'z') {
      object.rotation.x = -Math.PI / 2;
    } else if (verticalAxis === 'x') {
      object.rotation.z = Math.PI / 2;
    }

    object.updateMatrixWorld(true);
    const orientedBox = new THREE.Box3().setFromObject(object);
    const orientedSize = orientedBox.getSize(new THREE.Vector3());
    if (orientedSize.x > orientedSize.z * 1.22) {
      object.rotation.y += Math.PI / 2;
      object.updateMatrixWorld(true);
    }
  }

  function findHoopAnchor(root: THREE.Object3D): THREE.Vector3 | null {
    return findHoopAnchors(root)[0] ?? null;
  }

  function findHoopAnchors(root: THREE.Object3D): THREE.Vector3[] {
    const candidates: { node: THREE.Object3D; score: number }[] = [];
    root.traverse((node: THREE.Object3D) => {
      const label = (node.name || '').toLowerCase();
      if (!label) return;

      const hasHoopKeyword =
        label.includes('rim') ||
        label.includes('hoop') ||
        label.includes('net') ||
        label.includes('ring') ||
        label.includes('backboard');
      const isBasketballOnly = label.includes('basketball') && !hasHoopKeyword;
      if (isBasketballOnly) return;

      let score = 0;
      if (label.includes('rim')) score += 4;
      if (label.includes('hoop')) score += 4;
      if (label.includes('basket') && !label.includes('basketball')) score += 3;
      if (label.includes('ring')) score += 2;
      if (label.includes('net')) score += 1;
      if (label.includes('backboard')) score += 2;
      if (score <= 0) return;

      const nodeBox = new THREE.Box3().setFromObject(node);
      const nodeSize = nodeBox.getSize(new THREE.Vector3());
      const maxDim = Math.max(nodeSize.x, nodeSize.y, nodeSize.z);
      const minDim = Math.min(nodeSize.x, nodeSize.y, nodeSize.z);

      if (!Number.isFinite(maxDim) || maxDim <= 0) return;
      if (maxDim > 12 || minDim > 5) return;

      candidates.push({ node, score });
    });

    if (!candidates.length) return [];
    candidates.sort((a, b) => b.score - a.score);

    const anchors: THREE.Vector3[] = [];
    for (const candidate of candidates) {
      const position = candidate.node.getWorldPosition(new THREE.Vector3());
      const tooClose = anchors.some((anchor) => anchor.distanceTo(position) < 1.2);
      if (!tooClose) anchors.push(position);
      if (anchors.length >= 6) break;
    }

    return anchors;
  }

  function getPrimaryHoopPair(anchors: THREE.Vector3[]): [THREE.Vector3, THREE.Vector3] | null {
    if (anchors.length < 2) return null;

    let bestPair: [THREE.Vector3, THREE.Vector3] | null = null;
    let bestDistance = -1;
    for (let i = 0; i < anchors.length - 1; i += 1) {
      for (let j = i + 1; j < anchors.length; j += 1) {
        const distance = anchors[i].distanceTo(anchors[j]);
        if (distance > bestDistance) {
          bestDistance = distance;
          bestPair = [anchors[i], anchors[j]];
        }
      }
    }

    return bestPair;
  }

  function normalizeModelToCourt(root: THREE.Object3D) {
    const initialBox = new THREE.Box3().setFromObject(root);
    const center = initialBox.getCenter(new THREE.Vector3());
    root.position.x -= center.x;
    root.position.z -= center.z;
    root.position.y -= initialBox.min.y;
    root.updateMatrixWorld(true);

    let anchors = findHoopAnchors(root);
    const initialPair = getPrimaryHoopPair(anchors);
    if (!initialPair) {
      const fallbackBox = new THREE.Box3().setFromObject(root);
      courtFloorY = 0;
      courtMinX = -25;
      courtMaxX = 25;
      courtStartZ = 0;
      courtEndZ = 47;
      unitsPerFootX = 1;
      unitsPerFootZ = 1;
      zDirectionFromHoop = 1;
      shotOffsetX = 0;
      shotOffsetZ = 0;
      stadiumBounds = fallbackBox;
      return;
    }

    const [a0, b0] = initialPair;
    const direction0 = new THREE.Vector3(b0.x - a0.x, 0, b0.z - a0.z).normalize();
    const yaw = Math.atan2(direction0.x, direction0.z);
    root.rotation.y -= yaw;
    root.updateMatrixWorld(true);

    anchors = findHoopAnchors(root);
    const alignedPair = getPrimaryHoopPair(anchors);
    if (!alignedPair) return;

    const [a1, b1] = alignedPair;
    const hoopDistance = a1.distanceTo(b1) || 86;
    const courtScale = 86 / hoopDistance;
    root.scale.multiplyScalar(courtScale);
    root.updateMatrixWorld(true);

    anchors = findHoopAnchors(root);
    const scaledPair = getPrimaryHoopPair(anchors);
    if (!scaledPair) return;

    let nearHoop = scaledPair[0];
    let farHoop = scaledPair[1];
    if (farHoop.z < nearHoop.z) {
      nearHoop = scaledPair[1];
      farHoop = scaledPair[0];
    }

    root.position.x -= nearHoop.x;
    root.position.y += hoopWorldY - nearHoop.y;
    root.position.z -= nearHoop.z;
    root.updateMatrixWorld(true);

    const transformedBox = new THREE.Box3().setFromObject(root);
    courtFloorY = transformedBox.min.y;

    const translatedAnchors = findHoopAnchors(root);
    const translatedPair = getPrimaryHoopPair(translatedAnchors);
    if (translatedPair) {
      let near = translatedPair[0];
      let far = translatedPair[1];
      if (far.z < near.z) {
        near = translatedPair[1];
        far = translatedPair[0];
      }
      hoopAnchor = near;
      oppositeHoopAnchor = far;
    }

    unitsPerFootX = 1;
    unitsPerFootZ = 1;
    zDirectionFromHoop = 1;
    shotOffsetX = hoopAnchor ? hoopAnchor.x : 0;
    shotOffsetZ = hoopAnchor ? hoopAnchor.z : 0;
    courtMinX = -25;
    courtMaxX = 25;
    courtStartZ = 0;
    courtEndZ = 47;
    stadiumBounds = new THREE.Box3().setFromObject(root);
  }

  function clamp(value: number, minValue: number, maxValue: number): number {
    return Math.max(minValue, Math.min(maxValue, value));
  }

  function bezierPoint(t: number, start: Vec3, control: Vec3, end: Vec3): Vec3 {
    const inv = 1 - t;
    return {
      x: inv * inv * start.x + 2 * inv * t * control.x + t * t * end.x,
      y: inv * inv * start.y + 2 * inv * t * control.y + t * t * end.y,
      z: inv * inv * start.z + 2 * inv * t * control.z + t * t * end.z
    };
  }

  function buildWeightedBins(
    cells: HeatmapCell[],
    outcome: ShotOutcome,
    mode: 'league' | 'player',
    targetDistance: number | null
  ): WeightedBin[] {
    if (!cells.length) return [];

    return cells
      .map((cell) => {
        const attemptsForOutcome =
          outcome === 'made' ? cell.made : outcome === 'missed' ? cell.missed : cell.attempts;
        if (!attemptsForOutcome) return null;

        const distance = Math.hypot(cell.x, Math.max(0, cell.y - hoopDataY));

        return {
          x: cell.x,
          y: cell.y,
          distance,
          baseWeight: attemptsForOutcome
        };
      })
      .filter((bin): bin is WeightedBin => Boolean(bin));
  }

  function refillShotPool() {
    shotPool = currentBins.map((bin) => ({
      ...bin,
      remaining: Math.max(0, Math.floor(bin.baseWeight))
    }));
    shotPoolRemaining = shotPool.reduce((sum, bin) => sum + bin.remaining, 0);
  }

  function getRandomBinFromPool(): WeightedBin | null {
    if (!shotPoolRemaining || !shotPool.length) return null;

    let ticket = Math.floor(Math.random() * shotPoolRemaining);
    for (const bin of shotPool) {
      if (!bin.remaining) continue;

      if (ticket < bin.remaining) {
        bin.remaining -= 1;
        shotPoolRemaining -= 1;
        if (shotPoolRemaining === 0) {
          refillShotPool();
        }
        return bin;
      }

      ticket -= bin.remaining;
    }

    return null;
  }

  function pickShotOutcome(bin: WeightedBin, bins: WeightedBin[]): boolean {
    if (shotOutcome === 'made') return true;
    if (shotOutcome === 'missed') return false;

    const maxBaseWeight = bins.reduce((maxValue, current) => Math.max(maxValue, current.baseWeight), 1);
    const missPenalty = Math.min(0.35, bin.distance / 120);
    const baseline = 0.42 + 0.16 * (bin.baseWeight / maxBaseWeight);
    return Math.random() < Math.max(0.28, baseline - missPenalty);
  }

  function clearShots() {
    if (!scene) return;
    for (const shot of shots) {
      scene.remove(shot.ballMesh);
      scene.remove(shot.originMarker);
      scene.remove(shot.connectorLine);
      shot.connectorLine.geometry.dispose();
      (shot.connectorLine.material as THREE.Material).dispose();
    }
    shots = [];
  }

  function createBallInstance(made: boolean): THREE.Object3D {
    if (ballTemplate) {
      const instance = ballTemplate.clone(true);
      instance.scale.multiplyScalar(tuneBallScale);
      instance.traverse((node: THREE.Object3D) => {
        if (node instanceof THREE.Mesh) {
          node.castShadow = true;
          node.receiveShadow = true;
        }
      });
      return instance;
    }

    return new THREE.Mesh(
      new THREE.SphereGeometry(0.38 * tuneBallScale, 20, 20),
      new THREE.MeshStandardMaterial({ color: made ? 0xf59e0b : 0xfb923c, roughness: 0.7, metalness: 0.05 })
    );
  }

  function spawnShot() {
    if (!scene || !assetsReady || !currentBins.length) return;

    const bin = getRandomBinFromPool();
    if (!bin) return;

    const made = pickShotOutcome(bin, currentBins);
    const now = performance.now();

    const startFloor = dataToWorld(bin.x, bin.y);
    const start = {
      x: startFloor.x + (Math.random() - 0.5) * 0.6,
      y: courtFloorY + tuneFloorOffset + 7.6 + tuneReleaseHeight + Math.random() * 1.4 + shotVerticalNudge,
      z: startFloor.z + (Math.random() - 0.5) * 0.6
    };

    const mappedRim = dataToWorld(0, hoopDataY);
    const rim = hoopAnchor
      ? { x: hoopAnchor.x + tuneOffsetX, y: hoopAnchor.y + tuneRimHeightOffset, z: hoopAnchor.z + tuneOffsetZ }
      : { x: mappedRim.x, y: courtFloorY + tuneFloorOffset + effectiveRimHeight(), z: mappedRim.z };
    const outcomeSpread = Math.min(4.2, Math.max(1.2, bin.distance * 0.095));
    const end = {
      x: made ? rim.x : rim.x + (Math.random() - 0.5) * outcomeSpread,
      y: made ? rim.y + shotVerticalNudge : courtFloorY + tuneFloorOffset + 10 + tuneReleaseHeight + Math.random() * 1.4 + shotVerticalNudge,
      z: made ? rim.z : rim.z + (Math.random() - 0.25) * 2.6
    };
    end.y = made ? rim.y + shotVerticalNudge : courtFloorY + tuneFloorOffset + 10 + tuneReleaseHeight + Math.random() * 1.4 + shotVerticalNudge;

    const peakHeight = Math.max(13, Math.min(30, 11 + bin.distance * 0.3 + tuneArcHeight));
    const control = {
      x: (start.x + end.x) / 2,
      y: courtFloorY + tuneFloorOffset + peakHeight + shotVerticalNudge,
      z: (start.z + end.z) / 2
    };

    const ballMesh = createBallInstance(made);
    ballMesh.position.set(start.x, start.y, start.z);
    scene.add(ballMesh);

    const originMarker = new THREE.Mesh(originRingGeometry, made ? originMadeMaterial : originMissMaterial);
    originMarker.rotation.x = -Math.PI / 2;
    originMarker.position.set(startFloor.x, courtFloorY + tuneFloorOffset + 0.05, startFloor.z);
    originMarker.renderOrder = 20;
    scene.add(originMarker);

    const connectorGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(startFloor.x, courtFloorY + tuneFloorOffset + 0.18, startFloor.z),
      new THREE.Vector3(start.x, start.y, start.z)
    ]);
    const connectorLine = new THREE.Line(
      connectorGeometry,
      new THREE.LineBasicMaterial({
        color: made ? 0x2dd4bf : 0xfb923c,
        transparent: true,
        opacity: 0.34
      })
    );
    scene.add(connectorLine);

    shots = [
      ...shots.slice(-520),
      {
        start,
        control,
        end,
        startedAt: now,
        durationMs: Math.max(620, Math.min(1420, 700 + bin.distance * 17)) / Math.max(speed, 0.35),
        made,
        ballMesh,
        originMarker,
        connectorLine
      }
    ];
  }

  function updateShots(now: number) {
    if (!scene) return;

    const active: AnimatedShot[] = [];

    for (const shot of shots) {
      const elapsed = now - shot.startedAt;
      if (elapsed > shot.durationMs) {
        scene.remove(shot.ballMesh);
        scene.remove(shot.originMarker);
        scene.remove(shot.connectorLine);
        shot.connectorLine.geometry.dispose();
        (shot.connectorLine.material as THREE.Material).dispose();
        continue;
      }

      const t = clamp(elapsed / shot.durationMs, 0, 1);
      const point = bezierPoint(t, shot.start, shot.control, shot.end);
      shot.ballMesh.position.set(point.x, point.y, point.z);

      const from = new THREE.Vector3(
        shot.originMarker.position.x,
        courtFloorY + tuneFloorOffset + 0.18,
        shot.originMarker.position.z
      );
      const to = new THREE.Vector3(point.x, point.y, point.z);
      shot.connectorLine.geometry.setFromPoints([from, to]);

      const mat = shot.connectorLine.material as THREE.LineBasicMaterial;
      mat.opacity = 0.15 + (1 - t) * 0.35;

      active.push(shot);
    }

    shots = active;
  }

  function restartSeasonTimer() {
    if (seasonTimer) {
      clearInterval(seasonTimer);
      seasonTimer = null;
    }

    if (!playing || !loopSeasons || selectedSeason !== 'all' || timelineSeasons.length <= 1) {
      return;
    }

    const seasonDuration = Math.max(1300, Math.round(3600 / Math.max(speed, 0.35)));
    seasonTimer = setInterval(() => {
      if (!playing || !loopSeasons || selectedSeason !== 'all') return;
      activeSeasonIndex = (activeSeasonIndex + 1) % timelineSeasons.length;
      activeSeason = timelineSeasons[activeSeasonIndex] ?? '';
      clearShots();
      refillShotPool();
    }, seasonDuration);
  }

  function restartSpawnTimer() {
    if (spawnTimer) {
      clearInterval(spawnTimer);
      spawnTimer = null;
    }

    if (!playing || !currentBins.length || !assetsReady) {
      return;
    }

    const spawnDelay = Math.max(20, Math.round(46 / Math.max(speed, 0.35)));
    spawnTimer = setInterval(() => {
      if (!playing) return;
      const dynamicBurst = Math.max(
        4,
        Math.min(13, Math.round(baseBurstSize * Math.max(speed, 0.35) + currentBins.length / 320))
      );
      for (let count = 0; count < dynamicBurst; count += 1) {
        spawnShot();
      }
    }, spawnDelay);
  }

  async function loadAssets() {
    if (!scene) return;

    const [court, ball] = await Promise.all([
      loader.loadAsync(courtModelUrl),
      loader.loadAsync(ballModelUrl)
    ]);

    const loadedCourt = court.scene;
    if (!loadedCourt) return;
    orientCourtModel(loadedCourt);
    courtRoot = loadedCourt;

    scene.add(loadedCourt);
    loadedCourt.updateMatrixWorld(true);

    normalizeModelToCourt(loadedCourt);

    const normalizedCourtBox = new THREE.Box3().setFromObject(loadedCourt);

    if (camera && controls) {
      configureCenterCourtCamera(true);

      const size = normalizedCourtBox.getSize(new THREE.Vector3());
      controls.maxDistance = Math.max(controls.maxDistance, Math.min(size.x, size.z) * 0.35);

      const center = normalizedCourtBox.getCenter(new THREE.Vector3());
      if (center.y > courtFloorY + 25 && stadiumBounds) {
        stadiumBounds.min.y = courtFloorY - 1;
        stadiumBounds.max.y = Math.max(courtFloorY + 26, center.y + size.y * 0.1);
      }
      clampCameraInsideStadium();
    }

    const loadedBall = ball.scene;
    if (!loadedBall) return;
    ballTemplate = loadedBall;
    const ballBox = new THREE.Box3().setFromObject(loadedBall);
    const ballSize = ballBox.getSize(new THREE.Vector3());
    const maxDimension = Math.max(ballSize.x, ballSize.y, ballSize.z) || 1;
    const targetBallDiameter = 0.78;
    const scale = targetBallDiameter / maxDimension;
    loadedBall.scale.setScalar(scale);

    loadedBall.traverse((node: THREE.Object3D) => {
      if (node instanceof THREE.Mesh) {
        node.castShadow = true;
        node.receiveShadow = true;
      }
    });

    assetsReady = true;
    restartSpawnTimer();
  }

  function initScene() {
    scene = new THREE.Scene();
    scene.background = null;

    camera = new THREE.PerspectiveCamera(45, 1, 0.1, 500);
    camera.position.set(0, 35, 62);
    camera.lookAt(0, 6, 0);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    host.appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 6, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.enableZoom = false;
    controls.minDistance = 25;
    controls.maxDistance = 130;
    controls.maxPolarAngle = Math.PI * 0.495;

    const ambient = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambient);

    const directional = new THREE.DirectionalLight(0xffffff, 1.25);
    directional.position.set(20, 40, 15);
    directional.castShadow = true;
    scene.add(directional);

    const fill = new THREE.DirectionalLight(0x7dd3fc, 0.35);
    fill.position.set(-28, 16, -30);
    scene.add(fill);

    const shadowFloor = new THREE.Mesh(
      new THREE.PlaneGeometry(120, 120),
      new THREE.ShadowMaterial({ opacity: 0.24 })
    );
    shadowFloor.rotation.x = -Math.PI / 2;
    shadowFloor.position.y = -0.02;
    shadowFloor.receiveShadow = true;
    scene.add(shadowFloor);

    const resize = () => {
      if (!renderer || !camera) return;
      const width = host.clientWidth;
      const height = Math.max(420, host.clientHeight);
      renderer.setSize(width, height);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };

    resize();
    resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(host);
  }

  function animate(now: number) {
    if (!renderer || !scene || !camera) return;

    if (playing) {
      updateShots(now);
    }
    controls?.update();
    clampCameraInsideStadium();
    renderer.render(scene, camera);
    animationFrame = requestAnimationFrame(animate);
  }

  function resetView() {
    if (!camera || !controls) return;
    configureCenterCourtCamera(true);
  }

  onMount(async () => {
    initScene();
    await loadAssets().catch(() => {
      assetsReady = true;
      restartSpawnTimer();
    });
    animationFrame = requestAnimationFrame(animate);
  });

  onDestroy(() => {
    if (animationFrame) cancelAnimationFrame(animationFrame);
    if (seasonTimer) clearInterval(seasonTimer);
    if (spawnTimer) clearInterval(spawnTimer);

    clearShots();

    if (resizeObserver) resizeObserver.disconnect();
    controls?.dispose();
    renderer?.dispose();

    originRingGeometry.dispose();
    originMadeMaterial.dispose();
    originMissMaterial.dispose();

    if (renderer?.domElement && host?.contains(renderer.domElement)) {
      host.removeChild(renderer.domElement);
    }
  });
</script>

<div class="relative h-[38rem] w-full overflow-hidden rounded-2xl border border-white/10 bg-slate-950/70 lg:h-[calc(100vh-8rem)] lg:min-h-[44rem]">
  <div bind:this={host} class="h-full w-full"></div>

  <div class="pointer-events-none absolute left-3 top-3 rounded-xl border border-white/10 bg-slate-950/85 px-3 py-2 text-xs">
    <div class="font-semibold uppercase tracking-[0.18em] text-slate-400">3D Timeline</div>
    <div class="mt-1 text-sm font-semibold text-white">{activeSeason || 'No season data'}</div>
    <div class="mt-1 text-slate-400">
      {profileMode === 'player' && playerTargetDistance !== null
        ? `Player weighted - target ${playerTargetDistance.toFixed(1)} ft`
        : 'League weighted distribution'}
    </div>
  </div>

  {#if showControls}
    <div class="absolute right-3 top-3 rounded-xl border border-white/10 bg-slate-950/85 px-3 py-2 text-xs text-slate-300">
      <button
        type="button"
        class="rounded-md border border-white/10 px-2 py-1 font-semibold text-slate-200 transition hover:border-white/20 hover:text-white"
        on:click={resetView}
      >
        Reset View
      </button>
    </div>
  {/if}

  <div class="pointer-events-none absolute bottom-3 left-3 rounded-xl border border-white/10 bg-slate-950/85 px-3 py-2 text-xs text-slate-300">
    Drag to rotate. Page scroll stays active.
  </div>

  <div class="pointer-events-none absolute bottom-3 right-3 flex items-center gap-3 rounded-xl border border-white/10 bg-slate-950/85 px-3 py-2 text-xs text-slate-300">
    <span class="inline-flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-teal-400"></span>Made</span>
    <span class="inline-flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-orange-400"></span>Missed</span>
  </div>

  <div class="pointer-events-none absolute bottom-14 right-3 rounded-xl border border-white/10 bg-slate-950/85 px-3 py-2 text-xs text-slate-300">
    Rings on court show shot origin
  </div>
</div>

<style>
</style>
