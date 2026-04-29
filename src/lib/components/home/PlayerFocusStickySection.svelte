<script lang="ts">
  import PlayerDistanceChart from '$lib/components/PlayerDistanceChart.svelte';
  import Scroll from '$lib/components/Scroll.svelte';
  import { playerDistanceSummary, playerStoryCases } from '$lib/content/shotEvolutionStory';
  import type { PlayerDistanceSeries, ShotOutcome } from '$lib/types';

  export let players: PlayerDistanceSeries[] = [];

  let progress = 0;
  let playerDistanceOutcome: ShotOutcome = 'all';
  let selectedPlayer = 'LeBron James';

  function clampIndex(index: number) {
    return Math.max(0, Math.min(index, Math.max(playerStoryCases.length - 1, 0)));
  }

  function handlePlayerChange(event: Event) {
    selectedPlayer = (event.currentTarget as HTMLSelectElement).value;
  }

  function playerDistanceValue(
    row: PlayerDistanceSeries['seasons'][number],
    selectedOutcome: ShotOutcome
  ) {
    if (selectedOutcome === 'made') return row.avgMadeShotDistance;
    if (selectedOutcome === 'missed') return row.avgMissedShotDistance;
    return row.avgShotDistance;
  }

  function playerDistanceStats(series: PlayerDistanceSeries | null, selectedOutcome: ShotOutcome) {
    const seasons = series?.seasons ?? [];
    if (!seasons.length) return null;

    const rows = seasons.map((season) => ({
      season: season.season,
      value: playerDistanceValue(season, selectedOutcome)
    }));
    const peak = rows.reduce((best, row) => (row.value > best.value ? row : best), rows[0]);
    const low = rows.reduce((best, row) => (row.value < best.value ? row : best), rows[0]);
    const changes = rows.slice(1).map((row, index) => {
      const previous = rows[index];
      return {
        from: previous.season,
        to: row.season,
        delta: row.value - previous.value
      };
    });
    const biggestJump = changes.reduce(
      (best, change) => (!best || change.delta > best.delta ? change : best),
      null as { from: string; to: string; delta: number } | null
    );
    const biggestDrop = changes.reduce(
      (best, change) => (!best || change.delta < best.delta ? change : best),
      null as { from: string; to: string; delta: number } | null
    );

    return { peak, low, biggestJump, biggestDrop };
  }

  $: if (players.length && !players.some((player) => player.player === selectedPlayer)) {
    selectedPlayer = players[0].player;
  }
  $: selectedPlayerSeries = players.find((player) => player.player === selectedPlayer) ?? null;
  $: selectedPlayerStory =
    playerStoryCases.find((storyCase) => storyCase.player === selectedPlayer) ?? playerStoryCases[0];
  $: activeCaseIndex = clampIndex(playerStoryCases.findIndex((storyCase) => storyCase.player === selectedPlayer));
  $: selectedPlayerStats = playerDistanceStats(selectedPlayerSeries, playerDistanceOutcome);
  $: sharedPlayerDistanceValues = players.flatMap((player) =>
    player.seasons.map((season) => playerDistanceValue(season, playerDistanceOutcome))
  );
  $: sharedPlayerDistanceMax = sharedPlayerDistanceValues.length ? Math.max(...sharedPlayerDistanceValues) : 0;
  $: sharedPlayerDistanceDomain = {
    min: 0,
    max: Math.max(1, +(sharedPlayerDistanceMax * 1.12).toFixed(2))
  };
  $: playerDistanceLabel =
    playerDistanceOutcome === 'made' ? 'Made shots' : playerDistanceOutcome === 'missed' ? 'Missed shots' : 'All shots';
</script>

<section class="order-11 relative left-1/2 mt-10 w-screen -translate-x-1/2 px-4 sm:px-6 lg:px-8">
  <div class="mx-auto max-w-[118rem]">
    <Scroll
      bind:progress
      threshold={0.58}
      margin={8}
      storyWidth="minmax(20rem, 0.78fr)"
      vizWidth="minmax(0, 1.5fr)"
      gap="1.5rem"
    >
      {#snippet children()}
        <div class="space-y-6">
          <article class="player-story-card active panel min-h-[66vh] border border-teal-300/20 bg-slate-900/90 p-6 sm:p-8">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/80">{selectedPlayerStory?.label}</p>
            <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">{selectedPlayerStory?.title}</h2>
            <p class="mt-4 text-sm leading-7 text-slate-300">{selectedPlayerStory?.body}</p>
            <div class="mt-6 rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Player evidence</p>
              <p class="mt-2 text-xl font-bold text-white">{selectedPlayer}</p>
              <p class="mt-2 text-sm leading-6 text-slate-400">
                {playerDistanceSummary(selectedPlayerSeries)}
              </p>
            </div>
          </article>

          <article class="panel min-h-[66vh] border border-white/10 bg-slate-900/75 p-6 sm:p-8">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/70">Career range</p>
            <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">{selectedPlayer}&apos;s distance extremes.</h2>
            <p class="mt-4 text-sm leading-7 text-slate-300">
              We can see how shot distances change over time for specific players. Here are the peak and lowest average shot distances for the selected player, along with their biggest season-to-season jump and drop.
            </p>
            {#if selectedPlayerStats}
              <div class="mt-6 grid gap-4 sm:grid-cols-2">
                <div class="rounded-2xl border border-teal-300/20 bg-teal-400/10 px-4 py-4">
                  <p class="text-xs font-semibold uppercase tracking-[0.18em] text-teal-100">Peak distance</p>
                  <p class="mt-2 text-2xl font-bold text-white">{selectedPlayerStats.peak.value.toFixed(2)} ft</p>
                  <p class="mt-1 text-sm text-slate-300">{selectedPlayerStats.peak.season}</p>
                </div>

                <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                  <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Lowest distance</p>
                  <p class="mt-2 text-2xl font-bold text-white">{selectedPlayerStats.low.value.toFixed(2)} ft</p>
                  <p class="mt-1 text-sm text-slate-400">{selectedPlayerStats.low.season}</p>
                </div>
              </div>

              <div class="mt-4 grid gap-4 sm:grid-cols-2">
                <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                  <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Biggest jump</p>
                  <p class="mt-2 text-xl font-bold text-white">
                    {selectedPlayerStats.biggestJump ? `+${selectedPlayerStats.biggestJump.delta.toFixed(2)} ft` : 'N/A'}
                  </p>
                  <p class="mt-1 text-sm text-slate-400">
                    {selectedPlayerStats.biggestJump
                      ? `${selectedPlayerStats.biggestJump.from} to ${selectedPlayerStats.biggestJump.to}`
                      : 'No season-to-season change available'}
                  </p>
                </div>

                <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                  <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Biggest drop</p>
                  <p class="mt-2 text-xl font-bold text-white">
                    {selectedPlayerStats.biggestDrop ? `${selectedPlayerStats.biggestDrop.delta.toFixed(2)} ft` : 'N/A'}
                  </p>
                  <p class="mt-1 text-sm text-slate-400">
                    {selectedPlayerStats.biggestDrop
                      ? `${selectedPlayerStats.biggestDrop.from} to ${selectedPlayerStats.biggestDrop.to}`
                      : 'No season-to-season change available'}
                  </p>
                </div>
              </div>
            {/if}
          </article>
        </div>
      {/snippet}

      {#snippet viz()}
        <article class="panel w-full overflow-hidden border border-teal-300/20 bg-slate-900/90">
          <div class="grid gap-6 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-start lg:px-8">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/80">Player cases</p>
              <h3 class="mt-3 text-2xl font-bold text-white">{selectedPlayerStory?.title ?? 'Player distance trend'}</h3>
              <p class="mt-3 text-sm leading-6 text-slate-400">
                The selected player stays fixed while the career line reveals with scroll.
              </p>
            </div>

            <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
              <label class="flex items-center gap-3 text-sm text-slate-300">
                <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Player</span>
                <select
                  class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-teal-400/60"
                  value={selectedPlayer}
                  on:change={handlePlayerChange}
                >
                  {#each players as player}
                    <option value={player.player}>{player.player}</option>
                  {/each}
                </select>
              </label>
            </div>
          </div>

          <div class="border-b border-white/10 px-6 py-4 lg:px-8">
            <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <p class="text-sm leading-6 text-slate-400">
                {selectedPlayerStory?.label ?? 'Selected player'} | {playerDistanceLabel}
              </p>

              <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
                {#each [
                  { value: 'all', label: 'All Shots' },
                  { value: 'made', label: 'Made' },
                  { value: 'missed', label: 'Missed' }
                ] as option}
                  <button
                    type="button"
                    class:selected={playerDistanceOutcome === option.value}
                    class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
                    on:click={() => (playerDistanceOutcome = option.value as ShotOutcome)}
                  >
                    {option.label}
                  </button>
                {/each}
              </div>
            </div>
          </div>

          <div class="px-4 py-4 sm:px-6 lg:px-6">
            <PlayerDistanceChart
              player={selectedPlayerSeries}
              shotOutcome={playerDistanceOutcome}
              revealProgress={progress}
              yDomain={sharedPlayerDistanceDomain}
            />
          </div>
        </article>
      {/snippet}
    </Scroll>
  </div>
</section>

<style>
  button.selected {
    background: linear-gradient(135deg, rgba(45, 212, 191, 0.95), rgba(59, 130, 246, 0.85));
    color: #020617;
  }

  .player-story-card {
    transition:
      border-color 220ms ease,
      opacity 220ms ease,
      transform 220ms ease;
  }

  .player-story-card:not(.active) {
    opacity: 0.68;
  }

  .player-story-card.active {
    border-color: rgba(45, 212, 191, 0.44);
    transform: translateY(-2px);
  }
</style>
