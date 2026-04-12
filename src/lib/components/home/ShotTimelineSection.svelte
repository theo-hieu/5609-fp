<script lang="ts">
  import ShotTimeline3D from '$lib/components/ShotTimeline3D.svelte';
  import type { HeatmapPayload, PlayerDistanceSeries, ShotOutcome } from '$lib/types';

  export let heatmap: HeatmapPayload | null = null;
  export let seasons: string[] = [];
  export let players: PlayerDistanceSeries[] = [];

  let shot3dSeason = 'all';
  let shot3dPlayer = 'LeBron James';
  let shot3dOutcome: ShotOutcome = 'made';
  let shot3dProfileMode: 'league' | 'player' = 'league';
  let shot3dPlaying = true;
  let shot3dSpeed = 1;

  $: if (!shot3dPlayer && players.length) {
    shot3dPlayer = players[0].player;
  }

  $: shot3dPlayerSeasonOptions = (() => {
    const playerSeries = players.find((player) => player.player === shot3dPlayer);
    if (!playerSeries) return seasons;
    const seasonsSet = new Set(playerSeries.seasons.map((entry) => entry.season));
    return seasons.filter((season) => seasonsSet.has(season));
  })();

  $: shot3dPlayerCandidates = players.filter(
    (player) => shot3dSeason === 'all' || player.seasons.some((entry) => entry.season === shot3dSeason)
  );

  $: if (shot3dPlayerCandidates.length && !shot3dPlayerCandidates.some((player) => player.player === shot3dPlayer)) {
    shot3dPlayer = shot3dPlayerCandidates[0].player;
  }

  $: shot3dPlayerSeries = players.find((player) => player.player === shot3dPlayer) ?? null;

  $: selectedPlayerDistanceTarget = (() => {
    if (!shot3dPlayerSeries) return null;

    if (shot3dSeason !== 'all') {
      const matchingSeason = shot3dPlayerSeries.seasons.find((entry) => entry.season === shot3dSeason);
      return matchingSeason?.avgShotDistance ?? null;
    }

    if (!shot3dPlayerSeries.seasons.length) return null;

    const averageAcrossSeasons =
      shot3dPlayerSeries.seasons.reduce((sum, season) => sum + season.avgShotDistance, 0) /
      shot3dPlayerSeries.seasons.length;

    return +averageAcrossSeasons.toFixed(2);
  })();

  $: if (shot3dProfileMode === 'player' && !selectedPlayerDistanceTarget) {
    shot3dProfileMode = 'league';
  }

  const outcomeOptions: { value: ShotOutcome; label: string }[] = [
    { value: 'all', label: 'All Shots' },
    { value: 'made', label: 'Made' },
    { value: 'missed', label: 'Missed' }
  ];

  const profileModeOptions: { value: 'league' | 'player'; label: string }[] = [
    { value: 'league', label: 'League Mix' },
    { value: 'player', label: 'Player Weighted' }
  ];

  function seasonsForPlayer(playerName: string): string[] {
    const series = players.find((player) => player.player === playerName);
    if (!series) return [];

    const seasonSet = new Set(series.seasons.map((entry) => entry.season));
    return seasons.filter((season) => seasonSet.has(season));
  }

  function handleShot3dSeasonChange(event: Event) {
    const season = (event.currentTarget as HTMLSelectElement).value;
    shot3dSeason = season;

    const candidates = players.filter(
      (player) => season === 'all' || player.seasons.some((entry) => entry.season === season)
    );

    if (candidates.length && !candidates.some((player) => player.player === shot3dPlayer)) {
      shot3dPlayer = candidates[0].player;
    }
  }

  function handleShot3dPlayerChange(event: Event) {
    const player = (event.currentTarget as HTMLSelectElement).value;
    shot3dPlayer = player;

    const playerSeasons = seasonsForPlayer(player);
    if (shot3dSeason !== 'all' && !playerSeasons.includes(shot3dSeason)) {
      shot3dSeason = 'all';
    }
  }
</script>

<section class="mt-10">
  <article class="panel overflow-hidden border border-indigo-300/20 bg-slate-900/90">
    <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1.9fr)] lg:px-8">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-indigo-300/80">3D Shot Timeline</p>
        <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Animate shot paths through the season.</h2>
        <p class="mt-4 text-sm leading-7 text-slate-300">
          Watch shots arc toward the rim from a 3D half-court view. Select one season to focus, or leave it on all
          seasons to auto-play through the timeline. Enable player profile mode to approximate that player's shot
          distance tendencies using the available season-level distance data.
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <label class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4 text-sm text-slate-300">
          <span class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Season</span>
          <select
            class="mt-2 w-full rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-indigo-400/60"
            value={shot3dSeason}
            on:change={handleShot3dSeasonChange}
          >
            <option value="all">All seasons (timeline)</option>
            {#each shot3dPlayerSeasonOptions as season}
              <option value={season}>{season}</option>
            {/each}
          </select>
        </label>

        <label class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4 text-sm text-slate-300">
          <span class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Player profile</span>
          <select
            class="mt-2 w-full rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-indigo-400/60"
            value={shot3dPlayer}
            on:change={handleShot3dPlayerChange}
          >
            {#each shot3dPlayerCandidates as player}
              <option value={player.player}>{player.player}</option>
            {/each}
          </select>
        </label>
      </div>
    </div>

    <div class="border-b border-white/10 px-6 py-4 lg:px-8">
      <div class="flex flex-wrap items-center gap-3 text-sm">
        <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
          {#each outcomeOptions as option}
            <button
              type="button"
              class:selected={shot3dOutcome === option.value}
              class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
              on:click={() => (shot3dOutcome = option.value)}
            >
              {option.label}
            </button>
          {/each}
        </div>

        <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
          {#each profileModeOptions as option}
            <button
              type="button"
              class:selected={shot3dProfileMode === option.value}
              class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
              on:click={() => (shot3dProfileMode = option.value)}
              disabled={option.value === 'player' && !selectedPlayerDistanceTarget}
            >
              {option.label}
            </button>
          {/each}
        </div>

        <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
          <button
            type="button"
            class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
            on:click={() => (shot3dPlaying = !shot3dPlaying)}
          >
            {shot3dPlaying ? 'Pause' : 'Play'}
          </button>
        </div>

        <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
          {#each [0.75, 1, 1.5] as playbackRate}
            <button
              type="button"
              class:selected={shot3dSpeed === playbackRate}
              class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
              on:click={() => (shot3dSpeed = playbackRate)}
            >
              {playbackRate}x
            </button>
          {/each}
        </div>
      </div>
    </div>

    <div class="px-6 py-6 lg:px-8">
      <ShotTimeline3D
        {heatmap}
        {seasons}
        selectedSeason={shot3dSeason}
        shotOutcome={shot3dOutcome}
        profileMode={shot3dProfileMode}
        playerTargetDistance={selectedPlayerDistanceTarget}
        speed={shot3dSpeed}
        playing={shot3dPlaying}
      />
    </div>
  </article>
</section>

<style>
  button.selected {
    background: linear-gradient(135deg, rgba(129, 140, 248, 0.95), rgba(56, 189, 248, 0.85));
    color: #020617;
  }

  button:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }
</style>
