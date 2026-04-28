<script lang="ts">
  import type { ZoneSeasonTrend, ZoneShare, ZoneTrendPayload } from '$lib/types';

  export let zoneTrend: ZoneTrendPayload | null = null;

  type RecipeZone = {
    zone: string;
    label: string;
    share: number;
    fgPct: number;
    expectedPoints: number;
    attempts: number;
    color: string;
    pointValue: 2 | 3;
    path: string;
    labelX: number;
    labelY: number;
    anchorX: number;
    anchorY: number;
  };

  const orderedZones = [
    'Restricted Area',
    'In The Paint (Non-RA)',
    'Mid-Range',
    'Left Corner 3',
    'Right Corner 3',
    'Above the Break 3',
    'Backcourt'
  ];

  const zoneLabels: Record<string, string> = {
    'Restricted Area': 'Restricted Area',
    'In The Paint (Non-RA)': 'Paint, non-RA',
    'Mid-Range': 'Mid-Range',
    'Left Corner 3': 'Left Corner 3',
    'Right Corner 3': 'Right Corner 3',
    'Above the Break 3': 'Above Break 3',
    Backcourt: 'Backcourt'
  };

  const zoneColors: Record<string, string> = {
    'Restricted Area': '#fde68a',
    'In The Paint (Non-RA)': '#fb7185',
    'Mid-Range': '#fb923c',
    'Left Corner 3': '#38bdf8',
    'Right Corner 3': '#0ea5e9',
    'Above the Break 3': '#14b8a6',
    Backcourt: '#94a3b8'
  };

  let activeSeasonIndex = 0;
  let initialized = false;

  function fy(y: number) {
    return 47 - y + 4;
  }

  function zoneRow(row: ZoneSeasonTrend | null, zone: string): ZoneShare | null {
    return row?.zones.find((entry) => entry.zone === zone) ?? null;
  }

  function pointValueForZone(zone: string): 2 | 3 {
    return zone.includes('3') || zone === 'Backcourt' ? 3 : 2;
  }

  function zonePath(zone: string) {
    switch (zone) {
      case 'Restricted Area':
        return `M -4 ${fy(5.25)} A 4 4 0 0 1 4 ${fy(5.25)} L 4 ${fy(0)} L -4 ${fy(0)} Z`;
      case 'In The Paint (Non-RA)':
        return `M -8 ${fy(19)} L 8 ${fy(19)} L 8 ${fy(0)} L 4 ${fy(0)} L 4 ${fy(5.25)} A 4 4 0 0 0 -4 ${fy(5.25)} L -4 ${fy(0)} L -8 ${fy(0)} Z`;
      case 'Mid-Range':
        return `M -22 ${fy(14)} A 23.75 23.75 0 0 1 22 ${fy(14)} L 22 ${fy(0)} L 8 ${fy(0)} L 8 ${fy(19)} L -8 ${fy(19)} L -8 ${fy(0)} L -22 ${fy(0)} Z`;
      case 'Left Corner 3':
        return `M -25 ${fy(14)} L -22 ${fy(14)} L -22 ${fy(0)} L -25 ${fy(0)} Z`;
      case 'Right Corner 3':
        return `M 22 ${fy(14)} L 25 ${fy(14)} L 25 ${fy(0)} L 22 ${fy(0)} Z`;
      case 'Above the Break 3':
        return `M -25 4 L 25 4 L 25 ${fy(14)} L 22 ${fy(14)} A 23.75 23.75 0 0 0 -22 ${fy(14)} L -25 ${fy(14)} Z`;
      case 'Backcourt':
        return 'M -25 4 L 25 4 L 25 7 L -25 7 Z';
      default:
        return '';
    }
  }

  const labelPositions: Record<string, Pick<RecipeZone, 'labelX' | 'labelY' | 'anchorX' | 'anchorY'>> = {
    'Restricted Area': { labelX: -9.4, labelY: 46.2, anchorX: 0, anchorY: fy(4.6) },
    'In The Paint (Non-RA)': { labelX: 10.7, labelY: 39.8, anchorX: 6, anchorY: fy(12) },
    'Mid-Range': { labelX: -33.2, labelY: 31.5, anchorX: -13, anchorY: fy(18) },
    'Left Corner 3': { labelX: -41.2, labelY: 44.5, anchorX: -23.5, anchorY: fy(7) },
    'Right Corner 3': { labelX: 27.1, labelY: 44.5, anchorX: 23.5, anchorY: fy(7) },
    'Above the Break 3': { labelX: 18.2, labelY: 14.6, anchorX: 9, anchorY: fy(31) },
    Backcourt: { labelX: -41.2, labelY: 8.8, anchorX: -10, anchorY: 5.5 }
  };

  function buildRecipeZones(row: ZoneSeasonTrend | null): RecipeZone[] {
    return orderedZones.map((zone) => {
      const entry = zoneRow(row, zone);
      const pointValue = pointValueForZone(zone);
      const fgPct = entry?.fgPct ?? 0;
      const share = entry?.share ?? 0;
      const expectedPoints = fgPct * pointValue;
      const position = labelPositions[zone];

      return {
        zone,
        label: zoneLabels[zone] ?? zone,
        share,
        fgPct,
        expectedPoints,
        attempts: entry?.attempts ?? 0,
        color: zoneColors[zone] ?? '#e2e8f0',
        pointValue,
        path: zonePath(zone),
        ...position
      };
    });
  }

  function percent(value: number) {
    return `${(value * 100).toFixed(1)}%`;
  }

  function opacityForShare(share: number, maxShare: number) {
    if (!share) return 0.14;
    return Math.max(0.22, Math.min(0.82, 0.2 + (share / Math.max(maxShare, 0.0001)) * 0.62));
  }

  $: seasonRows = zoneTrend?.all ?? [];
  $: if (!initialized && seasonRows.length) {
    activeSeasonIndex = seasonRows.length - 1;
    initialized = true;
  }
  $: activeSeasonIndex = Math.max(0, Math.min(Number(activeSeasonIndex), Math.max(seasonRows.length - 1, 0)));
  $: activeSeason = seasonRows[activeSeasonIndex] ?? null;
  $: recipeZones = buildRecipeZones(activeSeason);
  $: maxShare = Math.max(0.01, ...recipeZones.map((zone) => zone.share));
  $: topZone = recipeZones.reduce((winner, zone) => (zone.share > winner.share ? zone : winner), recipeZones[0]);
  $: totalAttempts = activeSeason?.totalAttempts ?? 0;
</script>

<section class="order-7 mt-10">
  <article class="panel overflow-hidden border border-amber-300/20 bg-slate-900/90">
    <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1.35fr)] lg:px-8">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300/80">Modern shot recipe</p>
        <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Every season has a court recipe.</h2>
        <p class="mt-4 text-sm leading-7 text-slate-300">
          The terrain explains the reward. This labeled court shows the ingredients: which zones make up the shot mix,
          how often they are used, and what each zone returns.
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-3">
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Season</p>
          <p class="mt-2 text-2xl font-bold text-white">{activeSeason?.season ?? 'N/A'}</p>
          <p class="mt-1 text-sm text-slate-400">Scrub the recipe</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Top ingredient</p>
          <p class="mt-2 text-2xl font-bold text-white">{topZone?.label ?? 'N/A'}</p>
          <p class="mt-1 text-sm text-slate-400">{topZone ? percent(topZone.share) : '0.0%'} of attempts</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Attempts</p>
          <p class="mt-2 text-2xl font-bold text-white">{totalAttempts.toLocaleString()}</p>
          <p class="mt-1 text-sm text-slate-400">Zone-classified shots</p>
        </div>
      </div>
    </div>

    {#if seasonRows.length}
      <div class="border-b border-white/10 px-6 py-5 lg:px-8">
        <label class="grid gap-3 text-sm text-slate-300">
          <div class="flex items-center justify-between gap-4">
            <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Season scrubber</span>
            <span class="rounded-full border border-white/10 bg-slate-950/80 px-3 py-1 text-xs font-bold text-amber-100">
              {activeSeason?.season}
            </span>
          </div>
          <input
            type="range"
            min="0"
            max={Math.max(seasonRows.length - 1, 0)}
            step="1"
            bind:value={activeSeasonIndex}
            class="h-2 w-full accent-amber-300"
          />
          <div class="flex justify-between text-xs font-semibold text-slate-500">
            <span>{seasonRows[0]?.season}</span>
            <span>{seasonRows[seasonRows.length - 1]?.season}</span>
          </div>
        </label>
      </div>

      <div class="grid gap-6 px-4 py-5 lg:grid-cols-[minmax(0,1.35fr)_minmax(18rem,0.65fr)] lg:px-6 lg:py-6">
        <div class="recipe-frame overflow-hidden rounded-3xl border border-white/10 bg-slate-950/70 p-3 sm:p-5">
          <svg viewBox="-44 0 88 58" role="img" aria-label="Labeled half-court shot recipe by zone">
            <defs>
              <linearGradient id="recipe-floor" x1="0%" x2="0%" y1="0%" y2="100%">
                <stop offset="0%" stop-color="#0f172a" />
                <stop offset="100%" stop-color="#020617" />
              </linearGradient>
            </defs>

            <rect x="-44" y="0" width="88" height="58" rx="2" fill="url(#recipe-floor)" />
            <rect x="-25" y="4" width="50" height="47" rx="1.4" fill="rgba(148,163,184,0.05)" stroke="rgba(248,250,252,0.45)" stroke-width="0.18" />

            {#each recipeZones as zone}
              <path
                d={zone.path}
                fill={zone.color}
                fill-opacity={opacityForShare(zone.share, maxShare)}
                stroke="rgba(248,250,252,0.18)"
                stroke-width="0.18"
                class="zone-shape"
              />
            {/each}

            <g class="recipe-court-lines" aria-hidden="true">
              <line x1="-25" x2="25" y1={fy(0)} y2={fy(0)} />
              <line x1="-25" x2="-25" y1="4" y2={fy(0)} />
              <line x1="25" x2="25" y1="4" y2={fy(0)} />
              <rect x="-8" y={fy(19)} width="16" height="19" fill="none" />
              <path d={`M -6 ${fy(19)} A 6 6 0 0 1 6 ${fy(19)}`} fill="none" />
              <path d={`M -6 ${fy(19)} A 6 6 0 0 0 6 ${fy(19)}`} fill="none" stroke-dasharray="0.9 0.7" />
              <circle cx="0" cy={fy(5.25)} r="0.75" fill="none" />
              <line x1="-3" x2="3" y1={fy(4)} y2={fy(4)} />
              <path d={`M -4 ${fy(5.25)} A 4 4 0 0 1 4 ${fy(5.25)}`} fill="none" />
              <line x1="-22" x2="-22" y1={fy(0)} y2={fy(14)} />
              <line x1="22" x2="22" y1={fy(0)} y2={fy(14)} />
              <path d={`M -22 ${fy(14)} A 23.75 23.75 0 0 1 22 ${fy(14)}`} fill="none" />
              <circle cx="0" cy="4" r="6" fill="none" opacity="0.45" />
            </g>

            <g class="recipe-labels">
              {#each recipeZones as zone}
                <line x1={zone.anchorX} y1={zone.anchorY} x2={zone.labelX + 5.5} y2={zone.labelY - 1.1} />
                <rect x={zone.labelX} y={zone.labelY - 4.1} width="15.6" height="7.5" rx="1.2" />
                <text x={zone.labelX + 0.8} y={zone.labelY - 2.1} class="zone-name">{zone.label}</text>
                <text x={zone.labelX + 0.8} y={zone.labelY - 0.1}>{percent(zone.share)} share</text>
                <text x={zone.labelX + 0.8} y={zone.labelY + 1.8}>{(zone.fgPct * 100).toFixed(1)}% FG | {zone.expectedPoints.toFixed(2)} pts</text>
              {/each}
            </g>
          </svg>
        </div>

        <aside class="grid content-start gap-3">
          {#each recipeZones as zone}
            <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-sm font-bold text-white">{zone.label}</p>
                  <p class="mt-1 text-xs text-slate-400">{zone.attempts.toLocaleString()} attempts</p>
                </div>
                <span class="mt-1 h-3 w-3 shrink-0 rounded-full" style={`background: ${zone.color}; opacity: ${opacityForShare(zone.share, maxShare)};`}></span>
              </div>
              <div class="mt-3 grid grid-cols-3 gap-2 text-xs">
                <span class="rounded-xl border border-white/10 bg-slate-900/80 px-2 py-2 text-slate-300">
                  <b class="block text-white">{percent(zone.share)}</b>
                  Share
                </span>
                <span class="rounded-xl border border-white/10 bg-slate-900/80 px-2 py-2 text-slate-300">
                  <b class="block text-white">{(zone.fgPct * 100).toFixed(1)}%</b>
                  FG
                </span>
                <span class="rounded-xl border border-white/10 bg-slate-900/80 px-2 py-2 text-slate-300">
                  <b class="block text-white">{zone.expectedPoints.toFixed(2)}</b>
                  Pts
                </span>
              </div>
            </div>
          {/each}
        </aside>
      </div>
    {:else}
      <div class="px-6 py-6 lg:px-8">
        <div class="flex min-h-[24rem] items-center justify-center rounded-3xl border border-dashed border-white/10 bg-slate-950/70 text-sm text-slate-400">
          No zone trend data is available for the shot recipe.
        </div>
      </div>
    {/if}
  </article>
</section>

<style>
  .recipe-frame svg {
    display: block;
    width: 100%;
    height: auto;
    min-height: min(42rem, calc(100vh - 10rem));
  }

  .zone-shape {
    transition:
      fill-opacity 180ms ease,
      fill 180ms ease;
    vector-effect: non-scaling-stroke;
  }

  .recipe-court-lines {
    stroke: rgba(248, 250, 252, 0.68);
    stroke-width: 0.18;
    vector-effect: non-scaling-stroke;
  }

  .recipe-labels {
    font-size: 1.05px;
    font-weight: 750;
    letter-spacing: 0;
  }

  .recipe-labels line {
    stroke: rgba(248, 250, 252, 0.55);
    stroke-width: 0.15;
    vector-effect: non-scaling-stroke;
  }

  .recipe-labels rect {
    fill: rgba(2, 6, 23, 0.9);
    stroke: rgba(248, 250, 252, 0.18);
    stroke-width: 0.12;
    vector-effect: non-scaling-stroke;
  }

  .recipe-labels text {
    fill: #cbd5e1;
    stroke: none;
  }

  .recipe-labels .zone-name {
    fill: #f8fafc;
    font-size: 1.1px;
    font-weight: 900;
  }

  @media (max-width: 640px) {
    .recipe-frame {
      overflow-x: auto;
    }

    .recipe-frame svg {
      min-width: 48rem;
      min-height: 32rem;
    }
  }
</style>
