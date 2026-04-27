<script lang="ts">
  import DistanceChart from '$lib/components/DistanceChart.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import ShotTimeline3D from '$lib/components/ShotTimeline3D.svelte';
  import type {
    DistanceBucket,
    DistancePayload,
    FilterState,
    HeatmapPayload,
    PlayerDistanceSeries
  } from '$lib/types';

  export let seasons: string[] = [];
  export let distance: DistancePayload | null = null;
  export let heatmap: HeatmapPayload | null = null;
  export let players: PlayerDistanceSeries[] = [];

  let filter: FilterState = { shotOutcome: 'all', season: 'all' };
  let highlightThreePointRange = true;
  let mergedCharts = true;
  let shot3dProfileMode: 'league' | 'player' = 'league';
  let shot3dPlayer = 'LeBron James';
  let shot3dPlaying = true;
  let shot3dSpeed = 1;
  let shot3dLoop = true;

  function selectCollection<T>(collection: { all: T[]; bySeason: Record<string, T[]> } | null, season: string): T[] {
    if (!collection) return [];
    if (season === 'all') return collection.all;
    return collection.bySeason[season] ?? [];
  }

  function handleFilterChange(nextFilter: FilterState) {
    filter = nextFilter;
  }

  function seasonsForPlayer(playerName: string): string[] {
    const series = players.find((player) => player.player === playerName);
    if (!series) return [];

    const seasonSet = new Set(series.seasons.map((entry) => entry.season));
    return seasons.filter((season) => seasonSet.has(season));
  }

  function handleShot3dPlayerChange(event: Event) {
    const player = (event.currentTarget as HTMLSelectElement).value;
    shot3dPlayer = player;

    const playerSeasons = seasonsForPlayer(player);
    if (filter.season !== 'all' && !playerSeasons.includes(filter.season)) {
      filter = { ...filter, season: 'all' };
    }
  }

  $: selectedDistance = selectCollection<DistanceBucket>(distance, filter.season);
  $: shot3dPlayerSeries = players.find((player) => player.player === shot3dPlayer) ?? null;
  $: shot3dPlayerCandidates = players.filter(
    (player) => filter.season === 'all' || player.seasons.some((entry) => entry.season === filter.season)
  );
  $: if (!shot3dPlayer && players.length) {
    shot3dPlayer = players[0].player;
  }
  $: if (shot3dPlayerCandidates.length && !shot3dPlayerCandidates.some((player) => player.player === shot3dPlayer)) {
    shot3dPlayer = shot3dPlayerCandidates[0].player;
  }
  $: selectedPlayerDistanceTarget = (() => {
    if (!shot3dPlayerSeries) return null;

    if (filter.season !== 'all') {
      return shot3dPlayerSeries.seasons.find((entry) => entry.season === filter.season)?.avgShotDistance ?? null;
    }

    if (!shot3dPlayerSeries.seasons.length) return null;
    const average =
      shot3dPlayerSeries.seasons.reduce((sum, season) => sum + season.avgShotDistance, 0) /
      shot3dPlayerSeries.seasons.length;
    return +average.toFixed(2);
  })();
  $: if (shot3dProfileMode === 'player' && !selectedPlayerDistanceTarget) {
    shot3dProfileMode = 'league';
  }
</script>

<section class="order-10 mt-10">
  <article class="panel overflow-hidden border border-white/10 bg-slate-900/90">
    <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.35fr)] lg:px-8">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-300">Explore the data</p>
        <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Now test the story yourself.</h2>
        <p class="mt-4 text-sm leading-7 text-slate-300">
          The guided chapters fixed the viewpoint so the argument could build. This final panel gives the controls
          back: change seasons, compare made and missed shots, toggle the distance chart, or replay the court in 3D.
        </p>
      </div>

      <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
        <FilterBar {seasons} {filter} on:change={(event) => handleFilterChange(event.detail)} />
      </div>
    </div>

    <div class="grid gap-6 px-4 py-5 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)] lg:px-6 lg:py-6">
      <section class="overflow-hidden rounded-2xl border border-white/10 bg-slate-950/50">
        <div class="border-b border-white/10 px-5 py-4">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-amber-200">Distance profile</p>
              <p class="mt-2 text-sm leading-6 text-slate-400">Toggle the chart treatment while keeping the same shared filters.</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <button
                type="button"
                class:active-toggle={highlightThreePointRange}
                class="rounded-xl border border-white/10 bg-slate-950/90 px-3 py-2 text-xs font-bold uppercase tracking-[0.14em] text-slate-300 transition hover:border-amber-300/40 hover:text-white"
                on:click={() => (highlightThreePointRange = !highlightThreePointRange)}
              >
                3PT range
              </button>
              <button
                type="button"
                class:active-toggle={mergedCharts}
                class="rounded-xl border border-white/10 bg-slate-950/90 px-3 py-2 text-xs font-bold uppercase tracking-[0.14em] text-slate-300 transition hover:border-amber-300/40 hover:text-white"
                on:click={() => (mergedCharts = !mergedCharts)}
              >
                {mergedCharts ? 'Merged' : 'Split'}
              </button>
            </div>
          </div>
        </div>

        <div class="min-h-[32rem] px-4 py-5">
          <DistanceChart
            data={selectedDistance}
            shotOutcome={filter.shotOutcome}
            longDistanceBucket={distance?.metadata.longDistanceBucket ?? 40}
            bucketSize={distance?.metadata.bucketSize ?? 2}
            highlightThreePointRange={highlightThreePointRange}
            merged={mergedCharts}
          />
        </div>
      </section>

      <section class="overflow-hidden rounded-2xl border border-white/10 bg-slate-950/50">
        <div class="border-b border-white/10 px-5 py-4">
          <div class="flex flex-wrap items-end gap-3">
            <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
              {#each [
                { value: 'league', label: 'League' },
                { value: 'player', label: 'Player' }
              ] as option}
                <button
                  type="button"
                  class:selected={shot3dProfileMode === option.value}
                  class="rounded-xl px-3 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
                  on:click={() => (shot3dProfileMode = option.value as 'league' | 'player')}
                  disabled={option.value === 'player' && !selectedPlayerDistanceTarget}
                >
                  {option.label}
                </button>
              {/each}
            </div>

            <label class="flex min-w-0 items-center gap-2 text-sm text-slate-300">
              <span class="font-semibold uppercase tracking-[0.16em] text-slate-400">Player</span>
              <select
                class="w-44 max-w-[58vw] rounded-xl border border-white/10 bg-slate-950/90 px-3 py-2 text-sm text-white outline-none transition focus:border-indigo-400/60"
                value={shot3dPlayer}
                on:change={handleShot3dPlayerChange}
              >
                {#each shot3dPlayerCandidates as player}
                  <option value={player.player}>{player.player}</option>
                {/each}
              </select>
            </label>

            <label class="flex shrink-0 items-center gap-2 text-sm text-slate-300">
              <span class="font-semibold uppercase tracking-[0.16em] text-slate-400">Speed</span>
              <input type="range" min="0.5" max="2.5" step="0.1" bind:value={shot3dSpeed} class="h-2 w-28 accent-indigo-300" />
              <span class="w-10 text-right text-slate-300">{shot3dSpeed.toFixed(1)}x</span>
            </label>

            <div class="flex shrink-0 items-center gap-2 lg:ml-auto">
              <button
                type="button"
                class="rounded-xl border border-white/10 bg-slate-950/90 px-3 py-2 text-sm font-semibold text-slate-200 transition hover:border-white/20 hover:text-white"
                on:click={() => (shot3dPlaying = !shot3dPlaying)}
              >
                {shot3dPlaying ? 'Pause' : 'Play'}
              </button>
              <button
                type="button"
                class="rounded-xl border border-white/10 bg-slate-950/90 px-3 py-2 text-sm font-semibold text-slate-200 transition hover:border-white/20 hover:text-white"
                on:click={() => (shot3dLoop = !shot3dLoop)}
              >
                {shot3dLoop ? 'Loop' : 'Once'}
              </button>
            </div>
          </div>
        </div>

        <div class="p-3 sm:p-4">
          <ShotTimeline3D
            {heatmap}
            {seasons}
            selectedSeason={filter.season}
            shotOutcome={filter.shotOutcome}
            profileMode={shot3dProfileMode}
            playerTargetDistance={shot3dProfileMode === 'player' ? selectedPlayerDistanceTarget : null}
            speed={shot3dSpeed}
            playing={shot3dPlaying}
            loopSeasons={shot3dLoop}
            showControls={false}
          />
        </div>
      </section>
    </div>
  </article>
</section>

<style>
  button.selected {
    background: linear-gradient(135deg, rgba(129, 140, 248, 0.95), rgba(56, 189, 248, 0.85));
    color: #020617;
  }

  button.active-toggle {
    border-color: rgba(251, 191, 36, 0.55);
    color: #fde68a;
  }

  button:disabled {
    cursor: not-allowed;
    opacity: 0.45;
  }
</style>
