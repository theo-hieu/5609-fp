<script lang="ts">
  import ShotTimeline3D from '$lib/components/ShotTimeline3D.svelte';
  import type { HeatmapPayload, PlayerDistanceSeries, ShotOutcome } from '$lib/types';

  export let heatmap: HeatmapPayload | null = null;
  export let seasons: string[] = [];
  export let players: PlayerDistanceSeries[] = [];

  let shot3dSeason = 'all';
  let shot3dPlayer = 'LeBron James';
  let shot3dOutcome: ShotOutcome = 'all';
  let shot3dProfileMode: 'league' | 'player' = 'league';
  let shot3dPlaying = true;
  let shot3dSpeed = 1;
  let shot3dLoop = true;

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
</script>

<section class="order-9 mt-10">
  <article class="panel overflow-hidden border border-indigo-300/25 bg-slate-900/90">
    <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1.85fr)] lg:px-8">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-indigo-200/80">Recap in motion</p>
        <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Watch how shot distance changes over time with a 3d visualization.</h2>
          <p class="mt-4 text-sm leading-7 text-slate-300">
            This timeline shows every shot taken in the league across all seasons, shown on an actual court. With this, we are able to see the full evolution of shot distance and how it interacts with the court as a whole. Based off of this, we are able to determine how the league&apos;s center of gravity shifts over time and how that changes the strategic value of different court regions.
          </p>
          <p class="mt-3 text-sm leading-7 text-slate-400">
            Leave the timeline in the all seasons mode for a guided recap, then use the controls below to pause, replay, or
            compare specific seasons. Try selecting a player-weighted profile to see how a specifc player&apos;s shot distribution changes the story.
          </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div class="rounded-3xl border border-white/10 bg-slate-950/70 px-5 py-5">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Recap Scope</p>
          <p class="mt-3 text-2xl font-bold text-white">{shot3dSeason === 'all' ? 'All Seasons' : shot3dSeason}</p>
          <p class="mt-2 text-sm leading-6 text-slate-400">
            {shot3dProfileMode === 'player'
              ? 'Player mode weights shot distribution by the selected player profile for easier season-to-season comparison.'
              : 'League mode shows the full league distribution for the selected season scope.'}
          </p>
        </div>

        <div class="rounded-3xl border border-white/10 bg-slate-950/70 px-5 py-5">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">What to watch</p>
          <p class="mt-2 text-sm leading-6 text-slate-400">
            Teal arcs are makes and orange arcs are misses. The recap should feel like the you are watching the seasons in motion with
            fewer mid-range shots and more coming beyond the arc.
          </p>
        </div>
      </div>
    </div>

    <div class="border-b border-white/10 px-6 py-5 lg:px-8">
      <div class="flex flex-wrap items-end gap-4">
        <div class="inline-flex shrink-0 rounded-2xl border border-white/10 bg-slate-950/90 p-1">
          {#each [
            { value: 'all', label: 'All Shots' },
            { value: 'made', label: 'Made' },
            { value: 'missed', label: 'Missed' }
          ] as option}
            <button
              type="button"
              class:selected={shot3dOutcome === option.value}
              class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
              on:click={() => (shot3dOutcome = option.value as ShotOutcome)}
            >
              {option.label}
            </button>
          {/each}
        </div>

        <div class="inline-flex shrink-0 rounded-2xl border border-white/10 bg-slate-950/90 p-1">
          {#each [
            { value: 'league', label: 'League' },
            { value: 'player', label: 'Player weighted' }
          ] as option}
            <button
              type="button"
              class:selected={shot3dProfileMode === option.value}
              class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
              on:click={() => (shot3dProfileMode = option.value as 'league' | 'player')}
            >
              {option.label}
            </button>
          {/each}
        </div>

        <label class="flex min-w-0 items-center gap-3 text-sm text-slate-300">
          <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Season</span>
          <select
            class="w-44 max-w-[65vw] rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-indigo-400/60"
            bind:value={shot3dSeason}
            on:change={handleShot3dSeasonChange}
          >
            <option value="all">All seasons</option>
            {#each shot3dProfileMode === 'player' ? shot3dPlayerSeasonOptions : seasons as season}
              <option value={season}>{season}</option>
            {/each}
          </select>
        </label>

        {#if shot3dProfileMode === 'player'}
          <label class="flex min-w-0 items-center gap-3 text-sm text-slate-300">
            <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Player</span>
            <select
              class="w-52 max-w-[68vw] rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-indigo-400/60"
              bind:value={shot3dPlayer}
              on:change={handleShot3dPlayerChange}
            >
              {#each shot3dPlayerCandidates as player}
                <option value={player.player}>{player.player}</option>
              {/each}
            </select>
          </label>
        {/if}

        <label class="flex shrink-0 items-center gap-3 text-sm text-slate-300">
          <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Speed</span>
          <input
            type="range"
            min="0.5"
            max="2.5"
            step="0.1"
            bind:value={shot3dSpeed}
            class="h-2 w-32 accent-indigo-300"
          />
          <span class="w-10 text-right text-slate-300">{shot3dSpeed.toFixed(1)}x</span>
        </label>

        <div class="flex shrink-0 items-center gap-2 lg:ml-auto">
          <button
            type="button"
            class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-white/20 hover:text-white"
            on:click={() => (shot3dPlaying = !shot3dPlaying)}
          >
            {shot3dPlaying ? 'Pause' : 'Play'}
          </button>
          <button
            type="button"
            class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-white/20 hover:text-white"
            on:click={() => (shot3dLoop = !shot3dLoop)}
          >
            {shot3dLoop ? 'Repeat on' : 'Repeat off'}
          </button>
        </div>
      </div>
    </div>

    <div class="p-3 sm:p-4 lg:p-5">
      <ShotTimeline3D
        {heatmap}
        {seasons}
        selectedSeason={shot3dSeason}
        shotOutcome={shot3dOutcome}
        profileMode={shot3dProfileMode}
        playerTargetDistance={shot3dProfileMode === 'player' ? selectedPlayerDistanceTarget : null}
        speed={shot3dSpeed}
        playing={shot3dPlaying}
        loopSeasons={shot3dLoop}
        showControls={true}
      />
    </div>
  </article>
</section>

<style>
  button.selected {
    background: linear-gradient(135deg, rgba(129, 140, 248, 0.95), rgba(56, 189, 248, 0.85));
    color: #020617;
  }
</style>
