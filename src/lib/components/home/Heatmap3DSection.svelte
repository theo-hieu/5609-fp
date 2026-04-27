<script lang="ts">
  import CourtHeatmap3D from '$lib/components/CourtHeatmap3D.svelte';
  import type { HeatmapCell, HeatmapPayload, ShotOutcome } from '$lib/types';

  export let heatmap: HeatmapPayload | null = null;
  export let seasons: string[] = [];

  let heatmapSeason = 'all';
  let heatmap3dOutcome: ShotOutcome = 'all';

  function selectCollection<T>(collection: { all: T[]; bySeason: Record<string, T[]> } | null, season: string): T[] {
    if (!collection) return [];
    if (season === 'all') return collection.all;
    return collection.bySeason[season] ?? [];
  }

  function heatmapMetricValue(cell: HeatmapCell, outcome: ShotOutcome) {
    if (outcome === 'made') return cell.made;
    if (outcome === 'missed') return cell.missed;
    return cell.attempts;
  }

  $: selectedHeatmap = selectCollection<HeatmapCell>(heatmap, heatmapSeason);
  $: heatmapSeasonLabel = heatmapSeason === 'all' ? 'All Seasons' : heatmapSeason;
  $: heatmap3dLabel =
    heatmap3dOutcome === 'made' ? 'Made shots' : heatmap3dOutcome === 'missed' ? 'Missed shots' : 'All shots';
  $: heatmap3dPeakValue = selectedHeatmap.reduce(
    (best, cell) => Math.max(best, heatmapMetricValue(cell, heatmap3dOutcome)),
    0
  );
  $: heatmap3dActiveBins = selectedHeatmap.filter((cell) => heatmapMetricValue(cell, heatmap3dOutcome) > 0).length;
</script>

<section class="order-7 mt-10">
  <article class="panel overflow-hidden border border-sky-300/20 bg-slate-900/90">
    <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1.35fr)] lg:px-8">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-sky-300/80">Scene 3</p>
        <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Shots in 3D</h2>
          <p class="mt-4 text-sm leading-7 text-slate-300">
            Switch between all, made, and missed shots to compare how the same court geometry produces different
            landscapes. The rim stays dominant, but the corners and above-the-break arc change shape depending on
            whether you are looking at raw volume or only successful attempts.
          </p>
          <p class="mt-3 text-sm leading-7 text-slate-400">
            Taller bars mean more shots from that court location. The mid-range is the area inside the arc but away
            from the rim, which is why it often appears as quieter space in modern seasons.
          </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2">
        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Current Lens</p>
          <p class="mt-2 text-2xl font-bold text-white">{heatmap3dLabel}</p>
          <p class="mt-1 text-sm text-slate-400">{heatmapSeasonLabel}</p>
          <p class="mt-2 text-sm leading-6 text-slate-300">Bar height and color both use log scaling so dense hotspots do not overpower the rest of the floor.</p>
        </div>

        <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Active Grid</p>
          <p class="mt-2 text-2xl font-bold text-white">{heatmap3dActiveBins.toLocaleString()} bins</p>
          <p class="mt-1 text-sm text-slate-400">
            Peak cell: {heatmap3dPeakValue ? heatmap3dPeakValue.toLocaleString() : '0'}
          </p>
          <p class="mt-2 text-sm leading-6 text-slate-300">Hover any bar to inspect the exact attempts, makes, misses, and field goal percentage in that location.</p>
        </div>
      </div>
    </div>

    <div class="border-b border-white/10 px-6 py-5 lg:px-8">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
          {#each [
            { value: 'all', label: 'All Shots' },
            { value: 'made', label: 'Made' },
            { value: 'missed', label: 'Missed' }
          ] as option}
            <button
              type="button"
              class:selected={heatmap3dOutcome === option.value}
              class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
              on:click={() => (heatmap3dOutcome = option.value as ShotOutcome)}
            >
              {option.label}
            </button>
          {/each}
        </div>

        <label class="flex items-center gap-3 text-sm text-slate-300">
          <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Season</span>
          <select
            class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-sky-400/60"
            bind:value={heatmapSeason}
          >
            <option value="all">All seasons</option>
            {#each seasons as season}
              <option value={season}>{season}</option>
            {/each}
          </select>
        </label>
      </div>
    </div>

    <div class="min-h-[34rem] px-3 py-3 sm:px-4 sm:py-4 lg:min-h-[48rem] lg:px-5 lg:py-5">
      <CourtHeatmap3D
        cells={selectedHeatmap}
        shotOutcome={heatmap3dOutcome}
        cellSize={heatmap?.metadata.cellSize ?? 2}
        halfCourtLength={heatmap?.metadata.halfCourtLength ?? 47}
        halfCourtWidth={heatmap?.metadata.halfCourtWidth ?? 25}
      />
    </div>
  </article>
</section>

<style>
  button.selected {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.95), rgba(249, 115, 22, 0.85));
    color: #020617;
  }
</style>
