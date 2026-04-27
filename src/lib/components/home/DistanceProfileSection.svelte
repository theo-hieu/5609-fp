<script lang="ts">
  import DistanceChart from '$lib/components/DistanceChart.svelte';
  import type { DistanceBucket, DistancePayload, ShotOutcome } from '$lib/types';

  export let seasons: string[] = [];
  export let distance: DistancePayload | null = null;

  let shotOutcome: ShotOutcome = 'all';
  let distanceHighlightActive = true;
  let distanceChartsMerged = false;

  function selectCollection<T>(collection: { all: T[]; bySeason: Record<string, T[]> } | null, season: string): T[] {
    if (!collection) return [];
    if (season === 'all') return collection.all;
    return collection.bySeason[season] ?? [];
  }

  $: selectedDistance = selectCollection<DistanceBucket>(distance, 'all');
  $: headlineSeason = seasons.length ? `${seasons[0]} through ${seasons[seasons.length - 1]}` : 'All Seasons';
  $: shotOutcomeLabel = shotOutcome === 'all' ? 'All shots' : shotOutcome === 'made' ? 'Made shots' : 'Missed shots';
</script>

<section class="order-4 mt-10">
  <article class="panel overflow-hidden border border-amber-300/20 bg-slate-900/90">
    <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1.35fr)] lg:px-8">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300/80">Shot value changes the map</p>
        <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">The three-point line turns distance into strategy.</h2>
        <p class="mt-4 text-sm leading-7 text-slate-300">
          Shots near the rim are still the easiest to convert. The strange part is what happens farther away:
          attempts behind the arc can survive lower accuracy because they are worth an extra point. That boundary is
          the hinge of the whole story.
        </p>
        <p class="mt-3 text-sm leading-7 text-slate-400">
          This chapter keeps the full-league view fixed and highlights the three-point range, so the chart reads as
          evidence rather than a filter exercise.
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Guided Lens</p>
          <p class="mt-2 text-2xl font-bold text-white">{shotOutcomeLabel}</p>
          <p class="mt-1 text-sm text-slate-400">{headlineSeason}</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">What To Notice</p>
          <p class="mt-2 text-sm leading-6 text-slate-300">
            The highlighted region starts near the corner three distance. The league gives up some accuracy there,
            but the point value keeps those attempts central to modern offense.
          </p>
        </div>
      </div>
    </div>

    <div class="border-b border-white/10 px-6 py-5 lg:px-8">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="grid flex-1 gap-4 text-sm leading-6 text-slate-300 lg:grid-cols-3">
          <p class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
            <span class="font-semibold text-white">Rim:</span> highest conversion, still the cleanest shot on the floor.
          </p>
          <p class="rounded-2xl border border-amber-300/20 bg-amber-400/10 px-4 py-3">
            <span class="font-semibold text-amber-100">Arc:</span> lower accuracy can still work because the reward changes.
          </p>
          <p class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
            <span class="font-semibold text-white">Middle:</span> caught between easier twos and more valuable threes.
          </p>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            type="button"
            class:active-toggle={distanceHighlightActive}
            class="rounded-xl border border-white/10 bg-slate-950/90 px-3 py-2 text-xs font-bold uppercase tracking-[0.14em] text-slate-300 transition hover:border-amber-300/40 hover:text-white"
            on:click={() => (distanceHighlightActive = !distanceHighlightActive)}
          >
            3PT range
          </button>
          <button
            type="button"
            class:active-toggle={distanceChartsMerged}
            class="rounded-xl border border-white/10 bg-slate-950/90 px-3 py-2 text-xs font-bold uppercase tracking-[0.14em] text-slate-300 transition hover:border-amber-300/40 hover:text-white"
            on:click={() => (distanceChartsMerged = !distanceChartsMerged)}
          >
            {distanceChartsMerged ? 'Merged' : 'Split'}
          </button>
        </div>
      </div>
    </div>

    <div class="min-h-[32rem] px-6 py-6 lg:min-h-[44rem] lg:px-8">
      <DistanceChart
        data={selectedDistance}
        {shotOutcome}
        longDistanceBucket={distance?.metadata.longDistanceBucket ?? 40}
        bucketSize={distance?.metadata.bucketSize ?? 2}
        highlightThreePointRange={distanceHighlightActive}
        merged={distanceChartsMerged}
      />
    </div>
  </article>
</section>

<style>
  button.active-toggle {
    border-color: rgba(251, 191, 36, 0.55);
    color: #fde68a;
  }
</style>
