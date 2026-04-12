<script lang="ts">
  import PlayerDistanceChart from '$lib/components/PlayerDistanceChart.svelte';
  import type { PlayerDistanceSeries, ShotOutcome } from '$lib/types';

  export let players: PlayerDistanceSeries[] = [];

  let playerDistanceOutcome: ShotOutcome = 'all';
  let selectedPlayer = 'LeBron James';

  $: if (players.length && !players.some((player) => player.player === selectedPlayer)) {
    selectedPlayer = players[0].player;
  }

  $: selectedPlayerSeries = players.find((player) => player.player === selectedPlayer) ?? null;
  $: playerDistanceLabel =
    playerDistanceOutcome === 'made'
      ? 'Made shots'
      : playerDistanceOutcome === 'missed'
        ? 'Missed shots'
        : 'All shots';
  $: playerDistanceStatLabel =
    playerDistanceOutcome === 'made'
      ? 'Made-shot distance'
      : playerDistanceOutcome === 'missed'
        ? 'Missed-shot distance'
        : 'Average distance';
  $: selectedPlayerPeak = (selectedPlayerSeries?.seasons ?? []).reduce(
    (best, row) => {
      const value =
        playerDistanceOutcome === 'made'
          ? row.avgMadeShotDistance
          : playerDistanceOutcome === 'missed'
            ? row.avgMissedShotDistance
            : row.avgShotDistance;
      return !best || value > best.value ? { season: row.season, value } : best;
    },
    null as { season: string; value: number } | null
  );

  const outcomeOptions: { value: ShotOutcome; label: string }[] = [
    { value: 'all', label: 'All Shots' },
    { value: 'made', label: 'Made' },
    { value: 'missed', label: 'Missed' }
  ];
</script>

<section class="mt-10">
  <article class="panel overflow-hidden border border-teal-300/20 bg-slate-900/90">
    <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1.85fr)] lg:px-8">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/80">Player Focus</p>
        <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">
          How star players' shot profiles drifted over their careers.
        </h2>
        <p class="mt-4 text-sm leading-7 text-slate-300">
          Choose one featured player at a time to trace how their shot profile changed across seasons. The chart starts
          at that player's first shot attempt in the dataset and tracks the average distance of their shots throughout
          the years.
        </p>
        <div class="mt-5 flex flex-col gap-4 sm:flex-row sm:items-center">
          <label class="flex items-center gap-3 text-sm text-slate-300">
            <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Player</span>
            <select
              class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-teal-400/60"
              bind:value={selectedPlayer}
            >
              {#each players as player}
                <option value={player.player}>{player.player}</option>
              {/each}
            </select>
          </label>

          <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
            {#each outcomeOptions as option}
              <button
                type="button"
                class:selected={playerDistanceOutcome === option.value}
                class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
                on:click={() => (playerDistanceOutcome = option.value)}
              >
                {option.label}
              </button>
            {/each}
          </div>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Selected Player</p>
          <p class="mt-2 text-2xl font-bold text-white">{selectedPlayerSeries?.player ?? 'N/A'}</p>
          <p class="mt-1 text-sm text-slate-400">{playerDistanceLabel} view across this player's career arc</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Career Window</p>
          <p class="mt-2 text-2xl font-bold text-white">{selectedPlayerSeries?.firstSeason ?? 'N/A'}</p>
          <p class="mt-1 text-sm text-slate-400">
            {selectedPlayerPeak
              ? `Peak ${playerDistanceStatLabel.toLowerCase()}: ${selectedPlayerPeak.value.toFixed(2)} ft in ${selectedPlayerPeak.season}`
              : 'No player trend data available'}
          </p>
        </div>
      </div>
    </div>

    <div class="border-b border-white/10 px-6 py-4 text-sm text-slate-400 lg:px-8">
      Hover any point to compare {playerDistanceStatLabel.toLowerCase()} and shot volume for the selected player-season.
    </div>

    <div class="px-6 py-6 lg:px-8">
      <PlayerDistanceChart player={selectedPlayerSeries} shotOutcome={playerDistanceOutcome} />
    </div>
  </article>
</section>

<style>
  button.selected {
    background: linear-gradient(135deg, rgba(45, 212, 191, 0.95), rgba(59, 130, 246, 0.85));
    color: #020617;
  }
</style>
