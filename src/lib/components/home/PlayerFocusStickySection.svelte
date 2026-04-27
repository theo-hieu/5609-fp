<script lang="ts">
  import PlayerDistanceChart from '$lib/components/PlayerDistanceChart.svelte';
  import Scroll from '$lib/components/Scroll.svelte';
  import { playerDistanceSummary, playerStoryCases } from '$lib/content/shotEvolutionStory';
  import type { PlayerDistanceSeries, ShotOutcome } from '$lib/types';

  export let players: PlayerDistanceSeries[] = [];

  let progress = 0;
  let playerDistanceOutcome: ShotOutcome = 'all';
  let selectedPlayer = 'LeBron James';
  let manualSelection = false;

  function clampIndex(index: number) {
    return Math.max(0, Math.min(index, Math.max(playerStoryCases.length - 1, 0)));
  }

  function handlePlayerChange(event: Event) {
    selectedPlayer = (event.currentTarget as HTMLSelectElement).value;
    manualSelection = true;
  }

  $: activeCaseIndex = clampIndex(Math.floor((progress / 100) * playerStoryCases.length));
  $: activeCase = playerStoryCases[activeCaseIndex] ?? playerStoryCases[0];
  $: if (!manualSelection && activeCase) {
    selectedPlayer = activeCase.player;
  }
  $: if (players.length && !players.some((player) => player.player === selectedPlayer)) {
    selectedPlayer = players[0].player;
    manualSelection = false;
  }
  $: selectedPlayerSeries = players.find((player) => player.player === selectedPlayer) ?? null;
  $: selectedPlayerStory = playerStoryCases.find((storyCase) => storyCase.player === selectedPlayer) ?? activeCase;
  $: playerDistanceLabel =
    playerDistanceOutcome === 'made' ? 'Made shots' : playerDistanceOutcome === 'missed' ? 'Missed shots' : 'All shots';
</script>

<section class="order-8 relative left-1/2 mt-10 w-screen -translate-x-1/2 px-4 sm:px-6 lg:px-8">
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
          {#each playerStoryCases as storyCase, index}
            <article
              class:active={activeCaseIndex === index && !manualSelection}
              class="player-story-card panel min-h-[66vh] border border-teal-300/20 bg-slate-900/90 p-6 sm:p-8"
            >
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/80">{storyCase.label}</p>
              <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">{storyCase.title}</h2>
              <p class="mt-4 text-sm leading-7 text-slate-300">{storyCase.body}</p>
              <div class="mt-6 rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Player evidence</p>
                <p class="mt-2 text-xl font-bold text-white">{storyCase.player}</p>
                <p class="mt-2 text-sm leading-6 text-slate-400">
                  {playerDistanceSummary(players.find((player) => player.player === storyCase.player) ?? null)}
                </p>
              </div>
            </article>
          {/each}
        </div>
      {/snippet}

      {#snippet viz()}
        <article class="panel w-full overflow-hidden border border-teal-300/20 bg-slate-900/90">
          <div class="grid gap-6 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-start lg:px-8">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/80">Player cases</p>
              <h3 class="mt-3 text-2xl font-bold text-white">{selectedPlayerStory?.title ?? 'Player distance trend'}</h3>
              <p class="mt-3 text-sm leading-6 text-slate-400">
                {manualSelection
                  ? 'Manual player view is active. Use Follow story to return to scroll-driven player cases.'
                  : 'The chart follows the active story card as you scroll.'}
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

              {#if manualSelection}
                <button
                  type="button"
                  class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:border-teal-300/40 hover:text-white"
                  on:click={() => (manualSelection = false)}
                >
                  Follow story
                </button>
              {/if}
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

          <div class="px-4 py-6 sm:px-6 lg:px-8">
            <PlayerDistanceChart
              player={selectedPlayerSeries}
              shotOutcome={playerDistanceOutcome}
              revealProgress={manualSelection ? 100 : progress}
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
