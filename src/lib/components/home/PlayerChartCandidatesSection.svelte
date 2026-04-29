<script lang="ts">
  import CourtHeatmap from '$lib/components/CourtHeatmap.svelte';
  import type { HeatmapCell, PlayerDistanceSeries, PlayerHeatmapPayload } from '$lib/types';

  export let players: PlayerDistanceSeries[] = [];
  export let playerHeatmap: PlayerHeatmapPayload | null = null;

  type PlayerSummary = {
    player: string;
    color: string;
    attempts: number;
    made: number;
    avgShotDistance: number;
    avgMadeShotDistance: number;
    avgMissedShotDistance: number;
    seasonsPlayed: number;
    season?: string;
  };

  type MetricConfig = {
    key: keyof Pick<
      PlayerSummary,
      'avgShotDistance' | 'avgMadeShotDistance' | 'avgMissedShotDistance' | 'attempts' | 'made'
    >;
    label: string;
    shortLabel: string;
  };

  const featuredPlayers = [
    'LeBron James',
    'Stephen Curry',
    'James Harden',
    'Kevin Durant',
    'Nikola Jokic',
    'Luka Doncic',
    'Anthony Edwards',
    'Kobe Bryant',
    'Tim Duncan',
    'Giannis Antetokounmpo',
    "Shaquille O'Neal",
    'Jayson Tatum'
  ];
  const playerColors: Record<string, string> = {
    'LeBron James': '#8b5cf6',
    'Stephen Curry': '#fdb927',
    'James Harden': '#ce1141',
    'Kevin Durant': '#007ac1',
    'Nikola Jokic': '#fbbf24',
    'Luka Doncic': '#38bdf8',
    'Anthony Edwards': '#78be20',
    'Kobe Bryant': '#fdb927',
    'Tim Duncan': '#cbd5e1',
    'Giannis Antetokounmpo': '#10b981',
    "Shaquille O'Neal": '#60a5fa',
    'Jayson Tatum': '#22c55e'
  };

  const radarWidth = 360;
  const radarHeight = 328;
  const radarCenter = { x: 180, y: 166 };
  const radarRadius = 90;

  const radarMetrics: MetricConfig[] = [
    { key: 'avgShotDistance', label: 'Average shot distance', shortLabel: 'Avg dist' },
    { key: 'avgMadeShotDistance', label: 'Made-shot distance', shortLabel: 'Made dist' },
    { key: 'avgMissedShotDistance', label: 'Missed-shot distance', shortLabel: 'Miss dist' },
    { key: 'attempts', label: 'Shot attempts', shortLabel: 'Attempts' },
    { key: 'made', label: 'Made shots', shortLabel: 'Makes' }
  ];

  let selectedPlayer = 'Stephen Curry';
  let comparisonPlayer = 'LeBron James';
  let selectedScope = 'career';
  let hoveredRadarMetricIndex: number | null = null;
  let hoveredRadarPlayer: string | null = null;

  function playerSummary(series: PlayerDistanceSeries): PlayerSummary {
    const attempts = series.seasons.reduce((sum, season) => sum + season.attempts, 0);
    const made = series.seasons.reduce((sum, season) => sum + season.made, 0);
    const missed = series.seasons.reduce((sum, season) => sum + season.missed, 0);
    const weightedDistance = series.seasons.reduce(
      (sum, season) => sum + season.avgShotDistance * season.attempts,
      0
    );
    const weightedMadeDistance = series.seasons.reduce(
      (sum, season) => sum + season.avgMadeShotDistance * season.made,
      0
    );
    const weightedMissedDistance = series.seasons.reduce(
      (sum, season) => sum + season.avgMissedShotDistance * season.missed,
      0
    );

    return {
      player: series.player,
      color: playerColors[series.player] ?? '#cbd5e1',
      attempts,
      made,
      avgShotDistance: attempts ? weightedDistance / attempts : 0,
      avgMadeShotDistance: made ? weightedMadeDistance / made : 0,
      avgMissedShotDistance: missed ? weightedMissedDistance / missed : 0,
      seasonsPlayed: series.seasons.length
    };
  }

  function playerSeasonSummary(series: PlayerDistanceSeries | undefined, season: string): PlayerSummary | null {
    const row = series?.seasons.find((entry) => entry.season === season);
    if (!series || !row) return null;

    return {
      player: series.player,
      color: playerColors[series.player] ?? '#cbd5e1',
      attempts: row.attempts,
      made: row.made,
      avgShotDistance: row.avgShotDistance,
      avgMadeShotDistance: row.avgMadeShotDistance,
      avgMissedShotDistance: row.avgMissedShotDistance,
      seasonsPlayed: 1,
      season: row.season
    };
  }

  function clamp(value: number, min: number, max: number) {
    return Math.min(Math.max(value, min), max);
  }

  function scaleLinear(value: number, domainMin: number, domainMax: number, rangeMin: number, rangeMax: number) {
    const ratio = (value - domainMin) / Math.max(domainMax - domainMin, 0.0001);
    return rangeMin + clamp(ratio, 0, 1) * (rangeMax - rangeMin);
  }

  function metricValue(summary: PlayerSummary, key: MetricConfig['key']) {
    return summary[key];
  }

  function metricExtent(key: MetricConfig['key']) {
    const values = radarScaleProfiles.map((summary) => metricValue(summary, key));
    if (!values.length) return { min: 0, max: 1 };
    const min = Math.min(...values);
    const max = Math.max(...values);
    return {
      min: 0,
      max: Math.max(max, 0.0001)
    };
  }

  function computeLeagueSummary(profiles: PlayerSummary[]) {
    if (!profiles || !profiles.length) return null;
    const n = profiles.length;

    const avgShotDistance = profiles.reduce((s, p) => s + (p.avgShotDistance ?? 0), 0) / n;
    const avgMadeShotDistance = profiles.reduce((s, p) => s + (p.avgMadeShotDistance ?? 0), 0) / n;
    const avgMissedShotDistance = profiles.reduce((s, p) => s + (p.avgMissedShotDistance ?? 0), 0) / n;
    const attempts = profiles.reduce((s, p) => s + (p.attempts ?? 0), 0) / n;
    const made = profiles.reduce((s, p) => s + (p.made ?? 0), 0) / n;

    return {
      player: 'Player average',
      color: '#94a3b8',
      attempts,
      made,
      avgShotDistance,
      avgMadeShotDistance,
      avgMissedShotDistance,
      seasonsPlayed: 0,
      isLeague: true
    } as PlayerSummary & { isLeague?: boolean };
  }

  function radarPoint(index: number, radius: number) {
    const angle = -Math.PI / 2 + (index / radarMetrics.length) * Math.PI * 2;
    return {
      x: radarCenter.x + Math.cos(angle) * radius,
      y: radarCenter.y + Math.sin(angle) * radius
    };
  }

  function radarPath(summary: PlayerSummary) {
    const points = radarMetrics.map((_, index) => radarMetricPoint(summary, index));

    return `${points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(' ')} Z`;
  }

  function radarMetricPoint(summary: PlayerSummary, index: number) {
    const metric = radarMetrics[index];
    const extent = metricExtent(metric.key);
    const normalized = scaleLinear(metricValue(summary, metric.key), extent.min, extent.max, 0, 1);
    return radarPoint(index, radarRadius * normalized);
  }

  function radarTooltipPosition(index: number) {
    const point = radarPoint(index, radarRadius + 16);
    const tooltipWidth = 220;
    const tooltipHeight = 96;
    return {
      x: clamp(point.x + 16, 12, radarWidth - tooltipWidth - 12),
      y: clamp(point.y - tooltipHeight / 2, 12, radarHeight - tooltipHeight - 12),
      width: tooltipWidth,
      height: tooltipHeight
    };
  }

  function feet(value: number) {
    return `${value.toFixed(2)} ft`;
  }

  function compactNumber(value: number) {
    return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(value);
  }

  function formatMetric(summary: PlayerSummary, key: MetricConfig['key']) {
    if (key === 'attempts' || key === 'made') return compactNumber(metricValue(summary, key));
    return feet(metricValue(summary, key));
  }

  function scopeLabel(scope: string) {
    return scope === 'career' ? 'Career' : scope;
  }

  function playerHeatmapCells(playerName: string, scope: string): HeatmapCell[] {
    const series = playerHeatmap?.players.find((player) => player.player === playerName);
    if (!series) return [];
    if (scope === 'career') return series.all;
    return series.bySeason[scope] ?? [];
  }

  $: summaries = players
    .filter((player) => featuredPlayers.includes(player.player) && player.seasons.length)
    .map(playerSummary)
    .sort((a, b) => featuredPlayers.indexOf(a.player) - featuredPlayers.indexOf(b.player));
  $: if (summaries.length && !summaries.some((summary) => summary.player === selectedPlayer)) {
    selectedPlayer = summaries[0].player;
  }
  $: if (summaries.length && !summaries.some((summary) => summary.player === comparisonPlayer)) {
    comparisonPlayer = summaries[Math.min(1, summaries.length - 1)].player;
  }
  $: seasons = Array.from(
    new Set(
      players
        .filter((player) => featuredPlayers.includes(player.player))
        .flatMap((player) => player.seasons.map((season) => season.season))
    )
  );
  $: if (selectedScope !== 'career' && seasons.length && !seasons.includes(selectedScope)) {
    selectedScope = 'career';
  }
  $: selectedSummary = summaries.find((summary) => summary.player === selectedPlayer) ?? summaries[0] ?? null;
  $: comparisonSummary = summaries.find((summary) => summary.player === comparisonPlayer) ?? summaries[1] ?? summaries[0] ?? null;
  $: selectedSeries = players.find((player) => player.player === selectedPlayer);
  $: comparisonSeries = players.find((player) => player.player === comparisonPlayer);
  $: selectedSeasonSummary = selectedScope === 'career' ? selectedSummary : playerSeasonSummary(selectedSeries, selectedScope);
  $: comparisonSeasonSummary = selectedScope === 'career' ? comparisonSummary : playerSeasonSummary(comparisonSeries, selectedScope);
  $: leagueSummary = computeLeagueSummary(radarScaleProfiles);
  $: radarSummaries = [leagueSummary, comparisonSeasonSummary, selectedSeasonSummary].filter(Boolean) as (PlayerSummary & { isLeague?: boolean })[];
  $: selectedHeatmapCells = playerHeatmapCells(selectedPlayer, selectedScope);
  $: comparisonHeatmapCells = playerHeatmapCells(comparisonPlayer, selectedScope);
  $: playerHeatmapComparisons = [
    {
      player: selectedPlayer,
      color: selectedSummary?.color ?? '#cbd5e1',
      cells: selectedHeatmapCells
    },
    {
      player: comparisonPlayer,
      color: comparisonSummary?.color ?? '#cbd5e1',
      cells: comparisonHeatmapCells
    }
  ];
  $: radarScaleProfiles = [
    ...(selectedScope === 'career'
      ? summaries
      : players
          .filter((player) => featuredPlayers.includes(player.player))
          .map((player) => playerSeasonSummary(player, selectedScope))
          .filter(Boolean))
  ] as PlayerSummary[];
  $: hoveredRadarMetric = hoveredRadarMetricIndex == null ? null : radarMetrics[hoveredRadarMetricIndex] ?? null;
  $: hoveredRadarTooltip = hoveredRadarMetricIndex == null ? null : radarTooltipPosition(hoveredRadarMetricIndex);
</script>

<section class="order-12 mt-10">
  <article class="panel overflow-hidden border border-violet-300/20 bg-slate-900/90">
    <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.35fr)] lg:px-8">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-violet-200/80">Player chart candidates</p>
        <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Do stars adapt to the shot revolution differently?</h2>
        <p class="mt-4 text-sm leading-7 text-slate-300">
          From this section, we can see how individual players playstyles are shown and compared through the radar and heatmap. The radar gives a quick shape to how the player shoots, while the heatmap shows exactly where their shots are coming from. Both of these are useful for comparing players across eras and seeing how different styles adapt to the changing strategic landscape.
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Radar</p>
          <p class="mt-2 text-xl font-bold text-white">Profile comparison</p>
          <p class="mt-2 text-sm leading-6 text-slate-400">Useful for comparing older interior stars, midrange creators, and newer perimeter-heavy players.</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Team color coding</p>
          <p class="mt-2 text-xl font-bold text-white">Era identities</p>
          <p class="mt-2 text-sm leading-6 text-slate-400">Colors reference each player&apos;s most story-relevant team context.</p>
        </div>
      </div>
    </div>

    <div class="px-4 py-5 lg:px-6 lg:py-6">
      {#if summaries.length}
        <section class="mx-auto max-w-[105rem] overflow-hidden rounded-3xl border border-white/10 bg-slate-950/70">
          <div class="border-b border-white/10 px-5 py-4">
            <div class="grid gap-4 xl:grid-cols-[minmax(0,1fr)_auto] xl:items-start">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-violet-200">Player comparison board</p>
                <h3 class="mt-2 text-xl font-bold text-white">Profile shape and shot chart side by side</h3>
                <p class="mt-2 text-sm leading-6 text-slate-400">
                  Choose Career for the full player profile, or select a season to compare only that year. The radar
                  summarizes profile shape while the courts show where those shots happen.
                </p>
              </div>

              <div class="grid gap-3 sm:grid-cols-3 xl:min-w-[32rem]">
                <label class="grid gap-1 text-sm text-slate-300">
                  <span class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Scope</span>
                  <select
                    class="rounded-xl border border-white/10 bg-slate-950/90 px-3 py-2 text-sm text-white outline-none transition focus:border-violet-300/60"
                    bind:value={selectedScope}
                  >
                    <option value="career">Career</option>
                    {#each seasons as season}
                      <option value={season}>{season}</option>
                    {/each}
                  </select>
                </label>

                <label class="grid gap-1 text-sm text-slate-300">
                  <span class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Player A</span>
                  <select
                    class="rounded-xl border border-white/10 bg-slate-950/90 px-3 py-2 text-sm text-white outline-none transition focus:border-violet-300/60"
                    bind:value={selectedPlayer}
                  >
                    {#each summaries as summary}
                      <option value={summary.player}>{summary.player}</option>
                    {/each}
                  </select>
                </label>

                <label class="grid gap-1 text-sm text-slate-300">
                  <span class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Player B</span>
                  <select
                    class="rounded-xl border border-white/10 bg-slate-950/90 px-3 py-2 text-sm text-white outline-none transition focus:border-violet-300/60"
                    bind:value={comparisonPlayer}
                  >
                    {#each summaries as summary}
                      <option value={summary.player}>{summary.player}</option>
                    {/each}
                  </select>
                </label>
              </div>
            </div>
          </div>

          <div class="grid gap-4 px-4 py-5 xl:grid-cols-[minmax(20rem,0.78fr)_minmax(0,1fr)_minmax(0,1fr)]">
            <div class="rounded-2xl border border-white/10 bg-slate-900/70 p-3">
              <div class="mb-3 px-2">
                <p class="text-sm font-bold text-white">Radar profile</p>
                <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{scopeLabel(selectedScope)}</p>
              </div>

              <div class="overflow-x-auto">
                <svg viewBox={`0 0 ${radarWidth} ${radarHeight}`} class="mx-auto min-w-[20rem] max-w-[22rem]" role="img" aria-label="Radar chart comparing player shot profiles">
                  {#each [0.25, 0.5, 0.75, 1] as ring}
                    <path
                      d={`${radarMetrics.map((_, index) => {
                        const point = radarPoint(index, radarRadius * ring);
                        return `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`;
                      }).join(' ')} Z`}
                      fill="none"
                      stroke="rgba(148, 163, 184, 0.16)"
                    />
                  {/each}

                  {#each radarMetrics as metric, index}
                    {@const point = radarPoint(index, radarRadius)}
                    {@const labelPoint = radarPoint(index, radarRadius + 32)}
                    <line x1={radarCenter.x} y1={radarCenter.y} x2={point.x} y2={point.y} stroke="rgba(148, 163, 184, 0.18)" />
                    <text x={labelPoint.x} y={labelPoint.y} fill="#cbd5e1" font-size="10.5" font-weight="800" text-anchor="middle">{metric.shortLabel}</text>
                  {/each}

                  {#each radarSummaries as summary}
                    <path
                      d={radarPath(summary)}
                      fill={summary.color}
                      fill-opacity={summary.isLeague ? '0.12' : hoveredRadarPlayer && hoveredRadarPlayer !== summary.player ? '0.12' : '0.26'}
                      stroke={summary.color}
                      stroke-width={summary.isLeague ? '3' : hoveredRadarPlayer === summary.player ? '4' : '3'}
                      stroke-opacity={summary.isLeague ? '0.95' : hoveredRadarPlayer && hoveredRadarPlayer !== summary.player ? '0.62' : '1'}
                      stroke-dasharray={summary.isLeague ? '6 4' : undefined}
                    />
                    {#each radarMetrics as metric, index}
                      {@const point = radarMetricPoint(summary, index)}
                      <circle
                        cx={point.x}
                        cy={point.y}
                        r={hoveredRadarMetricIndex === index && hoveredRadarPlayer === summary.player ? 7 : 4.5}
                        fill="#020617"
                        stroke={summary.color}
                        stroke-width="2.4"
                        pointer-events="none"
                      />
                    {/each}
                  {/each}

                  {#each radarSummaries as summary}
                    {#each radarMetrics as metric, index}
                      {@const point = radarMetricPoint(summary, index)}
                      <g
                        role="button"
                        tabindex="0"
                        aria-label={`${summary.player} ${metric.label}: ${formatMetric(summary, metric.key)}`}
                        on:pointerenter={() => {
                          hoveredRadarMetricIndex = index;
                          hoveredRadarPlayer = summary.player;
                        }}
                        on:pointerleave={() => {
                          hoveredRadarMetricIndex = null;
                          hoveredRadarPlayer = null;
                        }}
                        on:focus={() => {
                          hoveredRadarMetricIndex = index;
                          hoveredRadarPlayer = summary.player;
                        }}
                        on:blur={() => {
                          hoveredRadarMetricIndex = null;
                          hoveredRadarPlayer = null;
                        }}
                      >
                        <circle cx={point.x} cy={point.y} r="18" fill="transparent" />
                      </g>
                    {/each}
                  {/each}

                  <g transform="translate(18 20)">
                    {#each radarSummaries as summary, index}
                      <g transform={`translate(0 ${index * 22})`}>
                        <circle cx="0" cy="0" r="5.5" fill={summary.color} />
                        <text x="12" y="4" fill="#f8fafc" font-size="12" font-weight="800">{summary.player}</text>
                      </g>
                    {/each}
                  </g>

                  {#if hoveredRadarMetric && hoveredRadarTooltip}
                    <g transform={`translate(${hoveredRadarTooltip.x} ${hoveredRadarTooltip.y})`} pointer-events="none">
                      <rect
                        width={hoveredRadarTooltip.width}
                        height={hoveredRadarTooltip.height}
                        rx="14"
                        fill="rgba(2, 6, 23, 0.95)"
                        stroke="rgba(226, 232, 240, 0.2)"
                      />
                      <text x="14" y="22" fill="#f8fafc" font-size="13" font-weight="900">{hoveredRadarMetric.label}</text>
                      {#each radarSummaries as summary, index}
                        <g transform={`translate(14 ${46 + index * 24})`}>
                          <circle cx="0" cy="-4" r="4" fill={summary.color} />
                          <text x="12" y="0" fill="#cbd5e1" font-size="11" font-weight="800">{summary.player}</text>
                          <text x={hoveredRadarTooltip.width - 28} y="0" fill="#f8fafc" font-size="11" font-weight="900" text-anchor="end">
                            {formatMetric(summary, hoveredRadarMetric.key)}
                          </text>
                        </g>
                      {/each}
                    </g>
                  {/if}
                </svg>
              </div>

              <div class="mt-3 grid gap-2">
                {#each radarSummaries as summary}
                  <div class="rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2">
                    <p class="text-xs font-bold text-white">{summary.player}</p>
                    <p class="mt-1 text-[0.72rem] leading-5 text-slate-400">
                      {feet(summary.avgShotDistance)} avg distance, {compactNumber(summary.attempts)} attempts
                    </p>
                  </div>
                {/each}
              </div>
            </div>

            {#each playerHeatmapComparisons as comparison (`${comparison.player}-${selectedScope}`)}
              <div class="rounded-2xl border border-white/10 bg-slate-900/70 p-3">
                <div class="mb-3 flex items-center justify-between gap-3 px-2">
                  <div class="flex items-center gap-2">
                    <span class="h-3 w-3 rounded-full" style={`background: ${comparison.color}`}></span>
                    <div>
                      <p class="text-sm font-bold text-white">{comparison.player}</p>
                      <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{scopeLabel(selectedScope)}</p>
                    </div>
                  </div>
                  <p class="text-xs font-semibold text-slate-400">{comparison.cells.length.toLocaleString()} bins</p>
                </div>

                <div class="h-[26rem] min-h-0 xl:h-[30rem]">
                  {#if comparison.cells.length}
                    <CourtHeatmap
                      cells={comparison.cells}
                      shotOutcome="all"
                      cellSize={playerHeatmap?.metadata.cellSize ?? 2}
                      halfCourtLength={playerHeatmap?.metadata.halfCourtLength ?? 47}
                      halfCourtWidth={playerHeatmap?.metadata.halfCourtWidth ?? 25}
                    />
                  {:else}
                    <div class="flex h-full items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-400">
                      No shot chart data for this player and scope.
                    </div>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </section>
      {:else}
        <div class="col-span-full flex min-h-[24rem] items-center justify-center rounded-3xl border border-dashed border-white/10 bg-slate-950/70 text-sm text-slate-400">
          No featured player data is available for these candidate charts.
        </div>
      {/if}
    </div>
  </article>
</section>
