<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three-stdlib';

  import type { HeatmapCell, ShotOutcome } from '$lib/types';

  export let cells: HeatmapCell[] = [];
  export let shotOutcome: ShotOutcome = 'all';
  export let cellSize = 2;
  export let halfCourtLength = 47;
  export let halfCourtWidth = 25;

  type OrbitControlsInstance = InstanceType<typeof OrbitControls>;

  type MetricConfig = {
    title: string;
    tooltipLabel: string;
    legendMinLabel: string;
    legendMaxLabel: string;
    legendNote: string;
    gradient: string;
    lowColor: string;
    midColor: string;
    highColor: string;
    getValue: (cell: HeatmapCell) => number;
    formatValue: (value: number) => string;
  };

  type RenderableCell = {
    cell: HeatmapCell;
    value: number;
    normalized: number;
    height: number;
    x: number;
    z: number;
  };

  const MIN_BAR_HEIGHT = 0.45;
  const MAX_BAR_HEIGHT = 19;

  const volumeColors = {
    low: '#e2e8f0',
    mid: '#38bdf8',
    high: '#075985'
  };
  const madeColors = {
    low: '#ecfccb',
    mid: '#22c55e',
    high: '#166534'
  };
  const missedColors = {
    low: '#fff7ed',
    mid: '#f97316',
    high: '#9a3412'
  };

  let host: HTMLDivElement;
  let scene: THREE.Scene | null = null;
  let camera: THREE.PerspectiveCamera | null = null;
  let renderer: THREE.WebGLRenderer | null = null;
  let controls: OrbitControlsInstance | null = null;
  let resizeObserver: ResizeObserver | null = null;
  let animationFrame = 0;
  let mounted = false;

  let courtGroup: THREE.Group | null = null;
  let barsGroup: THREE.Group | null = null;
  let hoveredCell: RenderableCell | null = null;
  let mousePos = { x: 0, y: 0 };
  let activeHoverMesh: THREE.Mesh | null = null;

  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2(2, 2);

  function buildGradient(colors: { low: string; mid: string; high: string }) {
    return `linear-gradient(90deg, ${colors.low}, ${colors.mid}, ${colors.high})`;
  }

  function getMetricConfig(nextCells: HeatmapCell[], outcome: ShotOutcome): MetricConfig {
    const maxAttempts = Math.max(...nextCells.map((cell) => cell.attempts), 1);
    const maxMade = Math.max(...nextCells.map((cell) => cell.made), 1);
    const maxMissed = Math.max(...nextCells.map((cell) => cell.missed), 1);

    if (outcome === 'made') {
      return {
        title: 'Made Shot Height',
        tooltipLabel: 'Made',
        legendMinLabel: '1',
        legendMaxLabel: maxMade.toLocaleString(),
        legendNote: 'Log-scaled color and height',
        gradient: buildGradient(madeColors),
        lowColor: madeColors.low,
        midColor: madeColors.mid,
        highColor: madeColors.high,
        getValue: (cell) => cell.made,
        formatValue: (value) => Math.round(value).toLocaleString()
      };
    }

    if (outcome === 'missed') {
      return {
        title: 'Missed Shot Height',
        tooltipLabel: 'Missed',
        legendMinLabel: '1',
        legendMaxLabel: maxMissed.toLocaleString(),
        legendNote: 'Log-scaled color and height',
        gradient: buildGradient(missedColors),
        lowColor: missedColors.low,
        midColor: missedColors.mid,
        highColor: missedColors.high,
        getValue: (cell) => cell.missed,
        formatValue: (value) => Math.round(value).toLocaleString()
      };
    }

    return {
      title: 'Shot Volume Height',
      tooltipLabel: 'Attempts',
      legendMinLabel: '1',
      legendMaxLabel: maxAttempts.toLocaleString(),
      legendNote: 'Log-scaled color and height',
      gradient: buildGradient(volumeColors),
      lowColor: volumeColors.low,
      midColor: volumeColors.mid,
      highColor: volumeColors.high,
      getValue: (cell) => cell.attempts,
      formatValue: (value) => Math.round(value).toLocaleString()
    };
  }

  function logNormalized(value: number, maxValue: number) {
    if (value <= 0) return 0;
    if (maxValue <= 1) return 1;
    return Math.log10(Math.max(1, value)) / Math.log10(maxValue);
  }

  function dataToWorld(x: number, y: number) {
    return {
      x,
      z: halfCourtLength / 2 - y
    };
  }

  function buildRenderableCells(nextCells: HeatmapCell[], nextMetricConfig: MetricConfig, nextCellSize: number): RenderableCell[] {
    const maxValue = Math.max(...nextCells.map((cell) => nextMetricConfig.getValue(cell)), 1);

    return nextCells
      .map((cell) => {
        const value = nextMetricConfig.getValue(cell);
        if (!value) return null;

        const normalized = logNormalized(value, maxValue);
        const center = dataToWorld(cell.x + nextCellSize / 2, cell.y + nextCellSize / 2);

        return {
          cell,
          value,
          normalized,
          height: MIN_BAR_HEIGHT + normalized * (MAX_BAR_HEIGHT - MIN_BAR_HEIGHT),
          x: center.x,
          z: center.z
        };
      })
      .filter((cell): cell is RenderableCell => Boolean(cell));
  }

  function lerpPalette(low: string, mid: string, high: string, t: number) {
    const clamped = Math.max(0, Math.min(t, 1));
    const start = new THREE.Color(clamped < 0.5 ? low : mid);
    const end = new THREE.Color(clamped < 0.5 ? mid : high);
    const blend = clamped < 0.5 ? clamped / 0.5 : (clamped - 0.5) / 0.5;
    return start.lerp(end, blend);
  }

  function makeLine(points: THREE.Vector3[], color = 0xf8fafc, opacity = 0.5) {
    return new THREE.Line(
      new THREE.BufferGeometry().setFromPoints(points),
      new THREE.LineBasicMaterial({
        color,
        transparent: true,
        opacity
      })
    );
  }

  function makeCircle(centerX: number, centerY: number, radius: number, startAngle = 0, endAngle = Math.PI * 2, segments = 64) {
    const points: THREE.Vector3[] = [];
    for (let index = 0; index <= segments; index += 1) {
      const t = startAngle + ((endAngle - startAngle) * index) / segments;
      const x = centerX + radius * Math.cos(t);
      const y = centerY + radius * Math.sin(t);
      const point = dataToWorld(x, y);
      points.push(new THREE.Vector3(point.x, 0.04, point.z));
    }
    return points;
  }

  function makeRect(minX: number, minY: number, width: number, height: number) {
    const corners = [
      dataToWorld(minX, minY),
      dataToWorld(minX + width, minY),
      dataToWorld(minX + width, minY + height),
      dataToWorld(minX, minY + height),
      dataToWorld(minX, minY)
    ];

    return corners.map((point) => new THREE.Vector3(point.x, 0.04, point.z));
  }

  function makeThreePointArc() {
    const radius = 23.75;
    const centerY = 5.25;
    const points: THREE.Vector3[] = [];

    for (let x = -22; x <= 22; x += 0.5) {
      const y = centerY + Math.sqrt(Math.max(0, radius * radius - x * x));
      const point = dataToWorld(x, y);
      points.push(new THREE.Vector3(point.x, 0.04, point.z));
    }

    return points;
  }

  function disposeMaterial(material: THREE.Material | THREE.Material[]) {
    if (Array.isArray(material)) {
      material.forEach((entry) => entry.dispose());
      return;
    }

    material.dispose();
  }

  function disposeGroup(group: THREE.Group | null) {
    if (!group) return;

    group.traverse((child) => {
      if (child instanceof THREE.Mesh || child instanceof THREE.Line) {
        child.geometry.dispose();
        disposeMaterial(child.material);
      }
    });

    scene?.remove(group);
  }

  function createCourtGroup() {
    const group = new THREE.Group();

    const floor = new THREE.Mesh(
      new THREE.PlaneGeometry(halfCourtWidth * 2, halfCourtLength),
      new THREE.MeshStandardMaterial({
        color: 0x0f172a,
        roughness: 0.94,
        metalness: 0.05
      })
    );
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    group.add(floor);

    const glowFloor = new THREE.Mesh(
      new THREE.PlaneGeometry(halfCourtWidth * 2.04, halfCourtLength * 1.04),
      new THREE.MeshBasicMaterial({
        color: 0x1e293b,
        transparent: true,
        opacity: 0.28
      })
    );
    glowFloor.rotation.x = -Math.PI / 2;
    glowFloor.position.y = -0.03;
    group.add(glowFloor);

    group.add(makeLine(makeRect(-halfCourtWidth, 0, halfCourtWidth * 2, halfCourtLength), 0xf8fafc, 0.52));
    group.add(makeLine(makeRect(-8, 0, 16, 19), 0xf8fafc, 0.45));
    group.add(makeLine(makeCircle(0, 5.25, 0.75), 0xf8fafc, 0.55));
    group.add(makeLine(makeCircle(0, 5.25, 4, 0, Math.PI), 0xf8fafc, 0.4));
    group.add(makeLine(makeCircle(0, 19, 6, 0, Math.PI), 0xf8fafc, 0.36));
    group.add(makeLine(makeCircle(0, 47, 6, Math.PI, Math.PI * 2), 0xf8fafc, 0.26));
    group.add(makeLine(makeThreePointArc(), 0xf8fafc, 0.5));

    const leftCorner = [
      dataToWorld(-22, 0),
      dataToWorld(-22, 14)
    ].map((point) => new THREE.Vector3(point.x, 0.04, point.z));
    const rightCorner = [
      dataToWorld(22, 0),
      dataToWorld(22, 14)
    ].map((point) => new THREE.Vector3(point.x, 0.04, point.z));
    const backboard = [
      dataToWorld(-3, 4),
      dataToWorld(3, 4)
    ].map((point) => new THREE.Vector3(point.x, 0.04, point.z));

    group.add(makeLine(leftCorner, 0xf8fafc, 0.5));
    group.add(makeLine(rightCorner, 0xf8fafc, 0.5));
    group.add(makeLine(backboard, 0xf8fafc, 0.48));

    return group;
  }

  function createBarsGroup() {
    const group = new THREE.Group();

    for (const renderable of renderableCells) {
      const geometry = new THREE.BoxGeometry(cellSize * 0.9, renderable.height, cellSize * 0.9);
      const color = lerpPalette(
        metricConfig.lowColor,
        metricConfig.midColor,
        metricConfig.highColor,
        renderable.normalized
      );
      const material = new THREE.MeshStandardMaterial({
        color,
        emissive: color.clone().multiplyScalar(0.18),
        roughness: 0.35,
        metalness: 0.12,
        transparent: true,
        opacity: 0.96
      });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.set(renderable.x, renderable.height / 2, renderable.z);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      mesh.userData.renderable = renderable;
      group.add(mesh);
    }

    return group;
  }

  function resetCamera() {
    if (!camera || !controls) return;

    const longestCourtEdge = Math.max(halfCourtLength, halfCourtWidth * 2);
    camera.position.set(0, Math.max(28, longestCourtEdge * 0.62), Math.max(32, halfCourtLength * 0.9));
    controls.target.set(0, 3.4, 0);
    controls.minDistance = 18;
    controls.maxDistance = 110;
    controls.minPolarAngle = Math.PI / 6;
    controls.maxPolarAngle = Math.PI / 2.05;
    controls.update();
  }

  function updateRendererSize() {
    if (!renderer || !camera || !host) return;

    const width = host.clientWidth;
    const height = Math.max(420, host.clientHeight);

    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }

  function rebuildScene() {
    if (!scene) return;

    hoveredCell = null;
    clearHoverState();

    disposeGroup(courtGroup);
    disposeGroup(barsGroup);

    courtGroup = createCourtGroup();
    barsGroup = createBarsGroup();

    scene.add(courtGroup);
    scene.add(barsGroup);
    resetCamera();
  }

  function clearHoverState() {
    if (!activeHoverMesh) return;

    const material = activeHoverMesh.material as THREE.MeshStandardMaterial;
    material.emissiveIntensity = 1;
    activeHoverMesh.scale.set(1, 1, 1);
    activeHoverMesh = null;
  }

  function applyHoverState(mesh: THREE.Mesh | null) {
    if (activeHoverMesh === mesh) return;

    clearHoverState();

    if (!mesh) return;

    const material = mesh.material as THREE.MeshStandardMaterial;
    material.emissiveIntensity = 1.85;
    mesh.scale.set(1.04, 1.02, 1.04);
    activeHoverMesh = mesh;
  }

  function updateMousePosition(event: PointerEvent) {
    if (!host) return;

    const rect = host.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const padding = 12;
    const tooltipWidth = 220;
    const tooltipHeight = 112;

    mousePos = {
      x: Math.min(Math.max(x + 16, padding), Math.max(padding, rect.width - tooltipWidth - padding)),
      y: Math.min(Math.max(y + 16, padding), Math.max(padding, rect.height - tooltipHeight - padding))
    };
  }

  function updateHoverFromPointer(event: PointerEvent) {
    if (!camera || !barsGroup || !renderer) return;

    const rect = renderer.domElement.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    updateMousePosition(event);

    raycaster.setFromCamera(pointer, camera);
    const [intersection] = raycaster.intersectObjects(barsGroup.children, false);
    const mesh = (intersection?.object as THREE.Mesh | undefined) ?? null;

    if (!mesh) {
      hoveredCell = null;
      applyHoverState(null);
      return;
    }

    hoveredCell = (mesh.userData.renderable as RenderableCell | undefined) ?? null;
    applyHoverState(mesh);
  }

  function initScene() {
    scene = new THREE.Scene();

    camera = new THREE.PerspectiveCamera(42, 1, 0.1, 300);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearAlpha(0);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    host.appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.enablePan = false;
    controls.enableZoom = false;
    controls.dampingFactor = 0.08;

    const ambient = new THREE.HemisphereLight(0xe2e8f0, 0x020617, 1.25);
    scene.add(ambient);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.35);
    keyLight.position.set(24, 36, 18);
    keyLight.castShadow = true;
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x67e8f9, 0.42);
    fillLight.position.set(-20, 18, -18);
    scene.add(fillLight);

    resizeObserver = new ResizeObserver(() => updateRendererSize());
    resizeObserver.observe(host);

    renderer.domElement.addEventListener('pointermove', updateHoverFromPointer);
    renderer.domElement.addEventListener('pointerleave', () => {
      hoveredCell = null;
      applyHoverState(null);
    });

    updateRendererSize();
  }

  function animate() {
    if (!renderer || !scene || !camera) return;

    controls?.update();
    renderer.render(scene, camera);
    animationFrame = requestAnimationFrame(animate);
  }

  $: metricConfig = getMetricConfig(cells, shotOutcome);
  $: renderableCells = buildRenderableCells(cells, metricConfig, cellSize);
  $: hoveredMetricValue = hoveredCell ? metricConfig.formatValue(hoveredCell.value) : '';

  $: if (mounted) {
    cells;
    shotOutcome;
    cellSize;
    halfCourtLength;
    halfCourtWidth;
    rebuildScene();
  }

  onMount(() => {
    initScene();
    mounted = true;
    rebuildScene();
    animationFrame = requestAnimationFrame(animate);
  });

  onDestroy(() => {
    if (animationFrame) cancelAnimationFrame(animationFrame);

    if (renderer) {
      renderer.domElement.removeEventListener('pointermove', updateHoverFromPointer);
    }

    resizeObserver?.disconnect();
    controls?.dispose();

    disposeGroup(courtGroup);
    disposeGroup(barsGroup);
    renderer?.dispose();

    if (renderer?.domElement && host?.contains(renderer.domElement)) {
      host.removeChild(renderer.domElement);
    }
  });
</script>

<div class="relative h-full min-h-0 w-full">
  <div class="pointer-events-none absolute left-4 top-4 z-10 w-full max-w-sm rounded-2xl border border-white/10 bg-slate-950/85 px-4 py-3 backdrop-blur">
    <p class="text-[0.7rem] font-semibold uppercase tracking-[0.22em] text-slate-400">{metricConfig.title}</p>
    <div class="mt-3 h-3 w-full overflow-hidden rounded-full border border-white/10" style={`background: ${metricConfig.gradient};`}></div>
    <div class="mt-2 flex items-center justify-between text-[0.72rem] font-medium text-slate-300">
      <span>{metricConfig.legendMinLabel}</span>
      <span>{metricConfig.legendMaxLabel}</span>
    </div>
    <p class="mt-2 text-[0.68rem] uppercase tracking-[0.18em] text-slate-500">{metricConfig.legendNote}</p>
  </div>

  <div bind:this={host} class="h-full min-h-[28rem] w-full overflow-hidden rounded-3xl bg-slate-950/70"></div>

  <div class="pointer-events-none absolute bottom-4 left-4 rounded-xl border border-white/10 bg-slate-950/85 px-3 py-2 text-xs text-slate-300">
    Drag to orbit. Page scroll stays active.
  </div>

  {#if !renderableCells.length}
    <div class="pointer-events-none absolute inset-0 flex items-center justify-center px-6">
      <div class="rounded-2xl border border-dashed border-white/10 bg-slate-950/90 px-5 py-4 text-sm text-slate-400">
        No non-zero heatmap bins are available for the current lens.
      </div>
    </div>
  {/if}

  {#if hoveredCell}
    <div
      class="pointer-events-none absolute z-20 w-[13.75rem] rounded-2xl border border-white/10 bg-slate-950/95 px-3 py-2.5 text-xs shadow-2xl shadow-slate-950/60 backdrop-blur"
      style={`left: ${mousePos.x}px; top: ${mousePos.y}px;`}
    >
      <div class="flex items-baseline justify-between gap-3">
        <p class="font-semibold text-white">{metricConfig.tooltipLabel}</p>
        <p class="text-sm font-bold text-cyan-300">{hoveredMetricValue}</p>
      </div>
      <div class="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 text-slate-300">
        <span>Attempts</span>
        <span class="text-right text-white">{hoveredCell.cell.attempts.toLocaleString()}</span>
        <span>Made</span>
        <span class="text-right text-white">{hoveredCell.cell.made.toLocaleString()}</span>
        <span>Missed</span>
        <span class="text-right text-white">{hoveredCell.cell.missed.toLocaleString()}</span>
        <span>FG%</span>
        <span class="text-right text-white">{(hoveredCell.cell.fgPct * 100).toFixed(1)}%</span>
      </div>
    </div>
  {/if}
</div>
