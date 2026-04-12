<script lang="ts">
  import SeasonDistanceChart from '$lib/components/SeasonDistanceChart.svelte';
  import type { SeasonDistanceTrend, ShotOutcome } from '$lib/types';

  export let data: SeasonDistanceTrend[] = [];

  let seasonDistanceOutcome: ShotOutcome = 'all';

  $: seasonDistanceLabel =
    seasonDistanceOutcome === 'made'
      ? 'Made shots'
      : seasonDistanceOutcome === 'missed'
        ? 'Missed shots'
        : 'All shots';
  $: seasonDistanceStatLabel =
    seasonDistanceOutcome === 'made'
      ? 'Made-shot distance'
      : seasonDistanceOutcome === 'missed'
        ? 'Missed-shot distance'
        : 'Average distance';
  $: seasonDistancePeak = data.reduce(
    (best, row) => {
      const value =
        seasonDistanceOutcome === 'made'
          ? row.avgMadeShotDistance
          : seasonDistanceOutcome === 'missed'
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
  <article class="panel overflow-hidden border border-amber-300/20 bg-slate-900/90">
    <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1.9fr)] lg:px-8">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300/80">Season Trend</p>
        <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Average shot distance over time.</h2>
        <p class="mt-4 text-sm leading-7 text-slate-300">
          This view summarizes every season with one number: the average distance, in feet, of all recorded shots. As
          teams leaned harder into spacing and 3-point volume, that average moved farther from the basket.
        </p>
        <div class="mt-5 inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
          {#each outcomeOptions as option}
            <button
              type="button"
              class:selected={seasonDistanceOutcome === option.value}
              class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
              on:click={() => (seasonDistanceOutcome = option.value)}
            >
              {option.label}
            </button>
          {/each}
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Lens</p>
          <p class="mt-2 text-2xl font-bold text-white">{seasonDistanceLabel}</p>
          <p class="mt-1 text-sm text-slate-400">Comparing the same seasons through a different shot outcome filter</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Peak Season</p>
          <p class="mt-2 text-2xl font-bold text-white">{seasonDistancePeak?.season ?? 'N/A'}</p>
          <p class="mt-1 text-sm text-slate-400">
            {seasonDistancePeak
              ? `${seasonDistanceStatLabel}: ${seasonDistancePeak.value.toFixed(2)} ft`
              : 'No season trend data available'}
          </p>
        </div>
      </div>
    </div>

    <div class="px-6 py-6 lg:px-8">
      <SeasonDistanceChart data={data} shotOutcome={seasonDistanceOutcome} />
    </div>
  </article>
</section>

<style>
  button.selected {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.95), rgba(249, 115, 22, 0.85));
    color: #020617;
  }
</style>
