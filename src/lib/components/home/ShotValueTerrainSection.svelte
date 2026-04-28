<script lang="ts">
  import * as d3 from 'd3';
  import type { HeatmapCell, HeatmapPayload } from '$lib/types';

  export let heatmap: HeatmapPayload | null = null;
  export let seasons: string[] = [];

  type TerrainCell = HeatmapCell & {
    centerX: number;
    centerY: number;
    expectedPoints: number;
    pointValue: 2 | 3;
    lowSample: boolean;
  };

  type TerrainContour = {
    value: number;
    path: string;
    fill: string;
    opacity: number;
  };

  const HOOP_X = 0;
  const HOOP_Y = 5.25;
  const THREE_POINT_RADIUS = 23.75;
  const CORNER_THREE_X = 22;
  const CORNER_THREE_Y = 14;
  const DEFAULT_CELL_SIZE = 2;
  const DEFAULT_HALF_COURT_LENGTH = 47;
  const DEFAULT_HALF_COURT_WIDTH = 25;
  const contourThresholds = [0.62, 0.72, 0.82, 0.92, 1.02, 1.12, 1.22, 1.32, 1.42];

  let selectedSeason = '';
  let showVolume = true;

  function selectCollection(collection: HeatmapPayload | null, season: string): HeatmapCell[] {
    if (!collection) return [];
    if (season === 'all') return collection.all;
    return collection.bySeason[season] ?? [];
  }

  function isThreePointCell(centerX: number, centerY: number) {
    const isCornerThree = Math.abs(centerX) >= CORNER_THREE_X && centerY <= CORNER_THREE_Y;
    const distanceFromHoop = Math.hypot(centerX - HOOP_X, centerY - HOOP_Y);
    const isAboveBreakThree = centerY > CORNER_THREE_Y && distanceFromHoop >= THREE_POINT_RADIUS;
    return isCornerThree || isAboveBreakThree;
  }

  function fy(y: number) {
    return halfCourtLength - y;
  }

  function cellKey(x: number, y: number) {
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  }

  function terrainColor(value: number) {
    if (value >= 1.32) return '#2dd4bf';
    if (value >= 1.18) return '#38bdf8';
    if (value >= 1.04) return '#fde68a';
    if (value >= 0.9) return '#fbbf24';
    if (value >= 0.76) return '#fb923c';
    return '#7f1d1d';
  }

  function metricForCells(cells: TerrainCell[]) {
    if (!cells.length) return null;

    const best = cells.reduce((winner, cell) => (cell.expectedPoints > winner.expectedPoints ? cell : winner), cells[0]);
    const totalAttempts = cells.reduce((sum, cell) => sum + cell.attempts, 0);
    const weightedValue = cells.reduce((sum, cell) => sum + cell.expectedPoints * cell.attempts, 0);
    const lowSampleCount = cells.filter((cell) => cell.lowSample).length;

    return {
      best,
      average: totalAttempts ? weightedValue / totalAttempts : 0,
      lowSampleCount,
      totalAttempts
    };
  }

  function buildTerrainContours(cells: TerrainCell[]): TerrainContour[] {
    if (!cells.length) return [];

    const minX = -halfCourtWidth - cellSize / 2;
    const width = halfCourtWidth * 2 + cellSize;
    const columns = Math.floor(width / cellSize) + 1;
    const rows = Math.floor(halfCourtLength / cellSize) + 1;
    const cellMap = new Map(cells.map((cell) => [cellKey(cell.x, cell.y), cell]));
    const values: number[] = [];

    for (let row = 0; row < rows; row += 1) {
      const screenY = row * cellSize;
      const courtY = Math.max(0, Math.min(halfCourtLength - 0.01, halfCourtLength - screenY));

      for (let column = 0; column < columns; column += 1) {
        const courtX = minX + column * cellSize;
        const lookupX = Math.floor(courtX / cellSize) * cellSize;
        const lookupY = Math.floor(courtY / cellSize) * cellSize;
        const cell = cellMap.get(cellKey(lookupX, lookupY));
        values.push(cell?.expectedPoints ?? 0);
      }
    }

    const projection = d3.geoIdentity().scale(cellSize).translate([minX, 0]);
    const path = d3.geoPath(projection);

    return d3
      .contours()
      .size([columns, rows])
      .thresholds(contourThresholds)
      .smooth(true)(values)
      .map((contour) => {
        const value = Number(contour.value);
        return {
          value,
          path: path(contour) ?? '',
          fill: terrainColor(value),
          opacity: Math.max(0.2, Math.min(0.72, 0.18 + value / 2.2))
        };
      })
      .filter((contour) => contour.path);
  }

  $: cellSize = heatmap?.metadata.cellSize ?? DEFAULT_CELL_SIZE;
  $: halfCourtLength = heatmap?.metadata.halfCourtLength ?? DEFAULT_HALF_COURT_LENGTH;
  $: halfCourtWidth = heatmap?.metadata.halfCourtWidth ?? DEFAULT_HALF_COURT_WIDTH;
  $: if (!selectedSeason && seasons.length) {
    selectedSeason = seasons[seasons.length - 1];
  }
  $: if (selectedSeason !== 'all' && seasons.length && !seasons.includes(selectedSeason)) {
    selectedSeason = seasons[seasons.length - 1];
  }
  $: rawCells = selectCollection(heatmap, selectedSeason || 'all');
  $: lowSampleThreshold = selectedSeason === 'all' ? 100 : 20;
  $: terrainCells = rawCells.map((cell) => {
    const centerX = cell.x + cellSize / 2;
    const centerY = cell.y + cellSize / 2;
    const pointValue = isThreePointCell(centerX, centerY) ? 3 : 2;

    return {
      ...cell,
      centerX,
      centerY,
      pointValue,
      lowSample: cell.attempts < lowSampleThreshold,
      expectedPoints: +(cell.fgPct * pointValue).toFixed(3)
    } satisfies TerrainCell;
  });
  $: terrainContours = buildTerrainContours(terrainCells);
  $: terrainMetric = metricForCells(terrainCells);
  $: maxAttempts = Math.max(1, ...terrainCells.map((cell) => cell.attempts));
  $: selectedSeasonLabel = selectedSeason === 'all' ? 'All seasons' : selectedSeason || 'Latest season';
</script>

<section class="order-7 mt-10">
  <article class="panel overflow-hidden border border-cyan-300/20 bg-slate-900/90">
    <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1.35fr)] lg:px-8">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300/80">Shot value terrain</p>
        <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">The court has a reward landscape.</h2>
        <p class="mt-4 text-sm leading-7 text-slate-300">
          The heatmap shows where shots gather. This view explains why: every bin becomes expected points, so rim
          accuracy and three-point value rise out of the floor while the in-between area stays flatter.
        </p>
        <p class="mt-3 text-sm leading-7 text-slate-400">
          The terrain is computed from the same shot cells as the heatmap. Cells behind the inferred arc use three
          points; everything else uses two.
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-3">
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Lens</p>
          <p class="mt-2 text-2xl font-bold text-white">{selectedSeasonLabel}</p>
          <p class="mt-1 text-sm text-slate-400">Expected points per shot</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Weighted Avg</p>
          <p class="mt-2 text-2xl font-bold text-white">
            {terrainMetric ? terrainMetric.average.toFixed(2) : '0.00'}
          </p>
          <p class="mt-1 text-sm text-slate-400">Points per attempt</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Low Sample</p>
          <p class="mt-2 text-2xl font-bold text-white">
            {terrainMetric ? terrainMetric.lowSampleCount.toLocaleString() : '0'}
          </p>
          <p class="mt-1 text-sm text-slate-400">Muted cells</p>
        </div>
      </div>
    </div>

    <div class="border-b border-white/10 px-6 py-5 lg:px-8">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <label class="flex items-center gap-3 text-sm text-slate-300">
            <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Season</span>
            <select
              class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-cyan-400/60"
              bind:value={selectedSeason}
            >
              <option value="all">All seasons</option>
              {#each seasons as season}
                <option value={season}>{season}</option>
              {/each}
            </select>
          </label>

          <button
            type="button"
            class:active-toggle={showVolume}
            class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:border-cyan-300/40 hover:text-white"
            on:click={() => (showVolume = !showVolume)}
          >
            {showVolume ? 'Volume on' : 'Volume off'}
          </button>
        </div>

        <div class="flex flex-wrap gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-slate-300">
          <span class="rounded-full border border-teal-300/25 bg-teal-400/10 px-3 py-1 text-teal-100">High value</span>
          <span class="rounded-full border border-amber-300/25 bg-amber-400/10 px-3 py-1 text-amber-100">Middle</span>
          <span class="rounded-full border border-orange-300/25 bg-orange-400/10 px-3 py-1 text-orange-100">Lower value</span>
        </div>
      </div>
    </div>

    <div class="grid gap-6 px-4 py-5 lg:grid-cols-[minmax(0,1.45fr)_minmax(18rem,0.55fr)] lg:px-6 lg:py-6">
      <div class="terrain-frame min-h-[34rem] overflow-hidden rounded-3xl border border-white/10 bg-slate-950/70 p-3 sm:p-5">
        {#if terrainCells.length}
          <svg viewBox="-26 0 52 47" role="img" aria-label="Expected points terrain over a half basketball court">
            <defs>
              <radialGradient id="terrain-rim-glow" cx="50%" cy="89%" r="26%">
                <stop offset="0%" stop-color="#fde68a" stop-opacity="0.45" />
                <stop offset="100%" stop-color="#fde68a" stop-opacity="0" />
              </radialGradient>
              <linearGradient id="terrain-depth" x1="0%" x2="0%" y1="0%" y2="100%">
                <stop offset="0%" stop-color="#0f172a" />
                <stop offset="100%" stop-color="#020617" />
              </linearGradient>
            </defs>

            <rect x="-26" y="0" width="52" height="47" rx="1.6" fill="url(#terrain-depth)" />
            <rect x="-26" y="0" width="52" height="47" rx="1.6" fill="url(#terrain-rim-glow)" />

            {#each terrainContours as contour}
              <path d={contour.path} fill={contour.fill} opacity={contour.opacity} />
            {/each}

            {#if showVolume}
              <g opacity="0.58">
                {#each terrainCells as cell}
                  <circle
                    cx={cell.centerX}
                    cy={fy(cell.centerY)}
                    r={Math.max(0.08, Math.min(0.72, Math.sqrt(cell.attempts / maxAttempts) * 0.92))}
                    fill={cell.lowSample ? 'rgba(226,232,240,0.22)' : cell.pointValue === 3 ? 'rgba(56,189,248,0.5)' : 'rgba(253,230,138,0.42)'}
                  />
                {/each}
              </g>
            {/if}

            <g class="court-lines" aria-hidden="true">
              <rect x="-25" y="0" width="50" height="47" fill="none" />
              <line x1="-25" x2="25" y1="47" y2="47" />
              <line x1="-25" x2="-25" y1="0" y2="47" />
              <line x1="25" x2="25" y1="0" y2="47" />
              <rect x="-8" y={fy(19)} width="16" height="19" fill="none" />
              <path d={`M -6 ${fy(19)} A 6 6 0 0 1 6 ${fy(19)}`} fill="none" />
              <path d={`M -6 ${fy(19)} A 6 6 0 0 0 6 ${fy(19)}`} fill="none" stroke-dasharray="0.9 0.7" />
              <circle cx="0" cy={fy(HOOP_Y)} r="0.75" fill="none" />
              <line x1="-3" x2="3" y1={fy(4)} y2={fy(4)} />
              <path d={`M -4 ${fy(HOOP_Y)} A 4 4 0 0 1 4 ${fy(HOOP_Y)}`} fill="none" />
              <line x1="-22" x2="-22" y1={fy(0)} y2={fy(CORNER_THREE_Y)} />
              <line x1="22" x2="22" y1={fy(0)} y2={fy(CORNER_THREE_Y)} />
              <path d={`M -22 ${fy(CORNER_THREE_Y)} A ${THREE_POINT_RADIUS} ${THREE_POINT_RADIUS} 0 0 1 22 ${fy(CORNER_THREE_Y)}`} fill="none" />
              <circle cx="0" cy="0" r="6" fill="none" opacity="0.45" />
            </g>

            <g class="terrain-labels">
              <path d={`M -1.6 ${fy(8.5)} L -7 ${fy(11)}`} />
              <text x="-19.8" y={fy(11.6)}>Rim: conversion lifts the floor</text>
              <path d={`M 9 ${fy(18)} L 16 ${fy(23)}`} />
              <text x="2.4" y={fy(24.6)}>Mid-range: capped at two</text>
              <path d={`M 14 ${fy(30)} L 19.5 ${fy(35)}`} />
              <text x="-3.8" y={fy(36.2)}>Arc: misses cost less when makes count 3</text>
            </g>
          </svg>
        {:else}
          <div class="flex h-full min-h-[28rem] items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-400">
            No heatmap cells are available for the selected terrain view.
          </div>
        {/if}
      </div>

      <aside class="grid content-start gap-4">
        <div class="rounded-3xl border border-white/10 bg-slate-950/70 px-5 py-5">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-200">How to read it</p>
          <p class="mt-3 text-sm leading-7 text-slate-300">
            Height is implied through contour bands. The brighter teal bands are higher expected value. Small dots show
            where the volume sits when the overlay is on.
          </p>
        </div>

        <div class="rounded-3xl border border-white/10 bg-slate-950/70 px-5 py-5">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Peak cell</p>
          <p class="mt-3 text-2xl font-bold text-white">
            {terrainMetric ? terrainMetric.best.expectedPoints.toFixed(2) : '0.00'} pts
          </p>
          <p class="mt-2 text-sm leading-6 text-slate-400">
            {terrainMetric
              ? `${terrainMetric.best.pointValue}PT zone, ${(terrainMetric.best.fgPct * 100).toFixed(1)}% FG, ${terrainMetric.best.attempts.toLocaleString()} attempts.`
              : 'No terrain data available.'}
          </p>
        </div>

        <div class="rounded-3xl border border-white/10 bg-slate-950/70 px-5 py-5">
          <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Low-sample rule</p>
          <p class="mt-3 text-sm leading-7 text-slate-300">
            Cells below {lowSampleThreshold.toLocaleString()} attempts are still included, but their volume markers are
            muted so outliers do not steal the story.
          </p>
        </div>
      </aside>
    </div>
  </article>
</section>

<style>
  button.active-toggle {
    border-color: rgba(103, 232, 249, 0.55);
    color: #a5f3fc;
  }

  .terrain-frame svg {
    display: block;
    width: 100%;
    height: auto;
    min-height: min(42rem, calc(100vh - 10rem));
  }

  .court-lines {
    stroke: rgba(248, 250, 252, 0.68);
    stroke-width: 0.18;
    vector-effect: non-scaling-stroke;
  }

  .terrain-labels {
    fill: #f8fafc;
    font-size: 1.05px;
    font-weight: 800;
    letter-spacing: 0;
    paint-order: stroke;
    stroke: rgba(2, 6, 23, 0.9);
    stroke-width: 0.28;
    vector-effect: non-scaling-stroke;
  }

  .terrain-labels path {
    fill: none;
    stroke: rgba(248, 250, 252, 0.68);
    stroke-width: 0.16;
    vector-effect: non-scaling-stroke;
  }

  @media (max-width: 640px) {
    .terrain-frame {
      overflow-x: auto;
    }

    .terrain-frame svg {
      min-width: 44rem;
      min-height: 32rem;
    }
  }
</style>
