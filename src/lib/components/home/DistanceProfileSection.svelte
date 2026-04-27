<script lang="ts">
  import DistanceChart from '$lib/components/DistanceChart.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import type { DistanceBucket, DistancePayload, FilterState } from '$lib/types';

  export let seasons: string[] = [];
  export let distance: DistancePayload | null = null;

  let filter: FilterState = { shotOutcome: 'all', season: 'all' };
  let distanceHighlightActive = false;
  let distanceChartsMerged = false;

  function selectCollection<T>(collection: { all: T[]; bySeason: Record<string, T[]> } | null, season: string): T[] {
    if (!collection) return [];
    if (season === 'all') return collection.all;
    return collection.bySeason[season] ?? [];
  }

  function handleFilterChange(nextFilter: FilterState) {
    filter = nextFilter;
  }

  $: selectedDistance = selectCollection<DistanceBucket>(distance, filter.season);
  $: headlineSeason = filter.season === 'all' ? 'All Seasons' : filter.season;
  $: shotOutcomeLabel =
    filter.shotOutcome === 'all' ? 'All shots' : filter.shotOutcome === 'made' ? 'Made shots' : 'Missed shots';
</script>

<section class="order-4 mt-10">
  <article class="panel overflow-hidden border border-amber-300/20 bg-slate-900/90">
    <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1.35fr)] lg:px-8">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300/80">Scene 1</p>
        <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Volume and efficiency by distance.</h2>
        <p class="mt-4 text-sm leading-7 text-slate-300">
          This chart makes the original tradeoff visible. Shots near the rim are converted at the highest rates,
          but volume does not stay there. As distance increases, accuracy drops, yet teams still keep a large diet
          of longer attempts because the value structure of the court changes at the three-point line.
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Current Lens</p>
          <p class="mt-2 text-2xl font-bold text-white">{shotOutcomeLabel}</p>
          <p class="mt-1 text-sm text-slate-400">{headlineSeason}</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">How To Read It</p>
          <p class="mt-2 text-sm leading-6 text-slate-300">
            The x-axis shows shot distance and each stacked bar splits attempts into made and missed shots.
            The 3PT range starts near 22 feet in the corners and a little farther out above the break.
          </p>
        </div>
      </div>
    </div>

    <div class="border-b border-white/10 px-6 py-5 lg:px-8">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div class="min-w-0 flex-1">
          <FilterBar {seasons} {filter} on:change={(event) => handleFilterChange(event.detail)} />
        </div>

        <div class="flex flex-wrap gap-3">
          <button
            type="button"
            class:active-highlight={distanceHighlightActive}
            class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:border-amber-300/40 hover:text-white"
            on:click={() => (distanceHighlightActive = !distanceHighlightActive)}
          >
            {distanceHighlightActive ? 'Hide 3PT Highlight' : 'Highlight 3PT Range'}
          </button>

          <button
            type="button"
            class:active-highlight={distanceChartsMerged}
            class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:border-amber-300/40 hover:text-white"
            on:click={() => (distanceChartsMerged = !distanceChartsMerged)}
          >
            {distanceChartsMerged ? 'Split Charts' : 'Merge Charts'}
          </button>
        </div>
      </div>
      <p class="mt-4 text-xs leading-6 text-slate-400">
        This shared filter drives the distance profile. The chart honors the selected shot lens and can emphasize
        three-point range; bucket share and FG% are available in the hover tooltip.
      </p>
    </div>

    <div class="min-h-[32rem] px-6 py-6 lg:min-h-[44rem] lg:px-8">
      <DistanceChart
        data={selectedDistance}
        shotOutcome={filter.shotOutcome}
        longDistanceBucket={distance?.metadata.longDistanceBucket ?? 40}
        bucketSize={distance?.metadata.bucketSize ?? 2}
        highlightThreePointRange={distanceHighlightActive}
        merged={distanceChartsMerged}
      />
    </div>
  </article>
</section>

<style>
  button.active-highlight {
    border-color: rgba(251, 191, 36, 0.55);
    color: #fde68a;
  }
</style>
