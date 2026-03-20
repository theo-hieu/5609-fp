<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  import type { FilterState, ShotOutcome } from '$lib/types';

  export let seasons: string[] = [];
  export let filter: FilterState;

  const dispatch = createEventDispatcher<{ change: FilterState }>();

  function updateShotOutcome(shotOutcome: ShotOutcome) {
    dispatch('change', { ...filter, shotOutcome });
  }

  function updateSeason(event: Event) {
    const season = (event.currentTarget as HTMLSelectElement).value;
    dispatch('change', { ...filter, season });
  }
</script>

<div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
  <div>
    <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Interactive Filters</p>
    <h2 class="mt-2 text-xl font-bold text-white">Slice the same aggregates in multiple ways</h2>
  </div>

  <div class="flex flex-col gap-4 sm:flex-row sm:items-center">
    <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
      {#each [
        { value: 'all', label: 'All Shots' },
        { value: 'made', label: 'Made' },
        { value: 'missed', label: 'Missed' }
      ] as option}
        <button
          type="button"
          class:selected={filter.shotOutcome === option.value}
          class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
          on:click={() => updateShotOutcome(option.value as ShotOutcome)}
        >
          {option.label}
        </button>
      {/each}
    </div>

    <label class="flex items-center gap-3 text-sm text-slate-300">
      <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Season</span>
      <select
        class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-amber-400/60"
        value={filter.season}
        on:change={updateSeason}
      >
        <option value="all">All seasons</option>
        {#each seasons as season}
          <option value={season}>{season}</option>
        {/each}
      </select>
    </label>
  </div>
</div>

<style>
  button.selected {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.95), rgba(249, 115, 22, 0.85));
    color: #020617;
  }
</style>
