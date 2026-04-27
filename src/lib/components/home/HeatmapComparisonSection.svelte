<script lang="ts">
  import CourtHeatmap from '$lib/components/CourtHeatmap.svelte';
  import Scroll from '$lib/components/Scroll.svelte';
  import type { HeatmapCell, HeatmapPayload } from '$lib/types';

  export let heatmap: HeatmapPayload | null = null;
  export let seasons: string[] = [];

  let progress = 0;
  let compareStart = '2003-04';
  let compareEnd = '2023-24';

  function selectCollection<T>(collection: { all: T[]; bySeason: Record<string, T[]> } | null, season: string): T[] {
    if (!collection) return [];
    if (season === 'all') return collection.all;
    return collection.bySeason[season] ?? [];
  }

  $: compareStart = seasons.includes(compareStart) ? compareStart : (seasons[0] ?? 'all');
  $: compareEnd = seasons.includes(compareEnd) ? compareEnd : (seasons[seasons.length - 1] ?? 'all');
  $: startCells = selectCollection<HeatmapCell>(heatmap, compareStart);
  $: endCells = selectCollection<HeatmapCell>(heatmap, compareEnd);
  $: fadeProgress = Math.max(0, Math.min((progress - 50) / 24, 1));
</script>

<section class="order-6 mt-10">
  <Scroll bind:progress threshold={0.48} margin={8}>
    {#snippet children()}
      <div>
        <article class="panel min-h-[140vh] border border-teal-300/20 bg-slate-900/90 p-6 sm:p-8">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/80">Scene 2</p>
          <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Compare the court before and after the shot revolution.</h2>
          <p class="mt-4 text-sm leading-7 text-slate-300">
            The heatmaps default to {compareStart} versus {compareEnd}, so the comparison has a clear reading path.
            Start at the rim, scan the above-the-break arc, check whether the corners changed, then look at how quiet
            the mid-range becomes.
          </p>

          <div class="mt-8 grid gap-4 sm:grid-cols-2">
            <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Before</p>
              <p class="mt-2 text-2xl font-bold text-white">{compareStart}</p>
              <p class="mt-1 text-sm text-slate-400">Earlier shot geography, before the three-point boom fully accelerates.</p>
            </div>

            <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">After</p>
              <p class="mt-2 text-2xl font-bold text-white">{compareEnd}</p>
              <p class="mt-1 text-sm text-slate-400">Modern spacing, with more visible activity around the arc.</p>
            </div>
          </div>

          <div class="mt-8 rounded-3xl border border-emerald-300/20 bg-emerald-400/10 px-5 py-5">
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-200">How to compare</p>
            <div class="mt-4 grid gap-3 text-sm leading-6 text-slate-200 sm:grid-cols-2">
              <p><span class="font-semibold text-white">Rim density:</span> both eras still value layups and dunks.</p>
              <p><span class="font-semibold text-white">Above the break:</span> this is where modern three-point volume expands most.</p>
              <p><span class="font-semibold text-white">Corners:</span> efficient and important, but less explosive than above-the-break growth.</p>
              <p><span class="font-semibold text-white">Mid-range:</span> compare the quiet interior space between the rim and arc.</p>
            </div>
          </div>

          <p class="mt-8 text-sm leading-7 text-slate-300">
            As you scroll, both seasons transition from all-shot density to made-shot density. That keeps the original
            volume-to-makes idea, but the side-by-side layout makes the time comparison much harder to miss.
          </p>
        </article>
      </div>
    {/snippet}

    {#snippet viz()}
      <article class="panel overflow-hidden border border-emerald-300/20 bg-slate-900/90">
        <div class="border-b border-white/10 px-6 py-5 lg:px-8">
          <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300/80">Scene 2</p>
              <h3 class="mt-2 text-2xl font-bold text-white">Guided heatmap comparison</h3>
              <p class="mt-2 text-sm leading-6 text-slate-400">
                {#if fadeProgress < 0.5}
                  Comparing all-shot volume across two eras
                {:else}
                  Comparing made-shot density across two eras
                {/if}
              </p>
            </div>

            <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
              <label class="flex items-center gap-3 text-sm text-slate-300">
                <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Before</span>
                <select
                  class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-emerald-400/60"
                  bind:value={compareStart}
                >
                  {#each seasons as season}
                    <option value={season}>{season}</option>
                  {/each}
                </select>
              </label>

              <label class="flex items-center gap-3 text-sm text-slate-300">
                <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">After</span>
                <select
                  class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-emerald-400/60"
                  bind:value={compareEnd}
                >
                  {#each seasons as season}
                    <option value={season}>{season}</option>
                  {/each}
                </select>
              </label>
            </div>
          </div>
        </div>

        <div class="grid gap-4 px-4 py-5 lg:grid-cols-2 lg:px-6 lg:py-6">
          {#each [
            { label: 'Before', season: compareStart, cells: startCells },
            { label: 'After', season: compareEnd, cells: endCells }
          ] as comparison}
            <div class="rounded-3xl border border-white/10 bg-slate-950/50 p-3">
              <div class="mb-3 flex items-center justify-between gap-3 px-2">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{comparison.label}</p>
                  <p class="mt-1 text-xl font-bold text-white">{comparison.season}</p>
                </div>
                <p class="rounded-full border border-white/10 bg-slate-900/90 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-emerald-200">
                  {fadeProgress < 0.5 ? 'All shots' : 'Made shots'}
                </p>
              </div>

              <div class="grid min-h-[28rem]">
                <div
                  class="col-start-1 row-start-1 h-full transition-opacity duration-500"
                  style={`opacity: ${1 - fadeProgress}; pointer-events: ${fadeProgress < 0.98 ? 'auto' : 'none'}; z-index: ${fadeProgress < 0.98 ? 20 : 10};`}
                >
                  <CourtHeatmap
                    cells={comparison.cells}
                    shotOutcome="all"
                    cellSize={heatmap?.metadata.cellSize ?? 2}
                    halfCourtLength={heatmap?.metadata.halfCourtLength ?? 47}
                    halfCourtWidth={heatmap?.metadata.halfCourtWidth ?? 25}
                  />
                </div>

                <div
                  class="col-start-1 row-start-1 h-full transition-opacity duration-500"
                  style={`opacity: ${fadeProgress}; pointer-events: ${fadeProgress >= 0.98 ? 'auto' : 'none'}; z-index: ${fadeProgress >= 0.98 ? 20 : 10};`}
                >
                  <CourtHeatmap
                    cells={comparison.cells}
                    shotOutcome="made"
                    cellSize={heatmap?.metadata.cellSize ?? 2}
                    halfCourtLength={heatmap?.metadata.halfCourtLength ?? 47}
                    halfCourtWidth={heatmap?.metadata.halfCourtWidth ?? 25}
                  />
                </div>
              </div>
            </div>
          {/each}
        </div>
      </article>
    {/snippet}
  </Scroll>
</section>
