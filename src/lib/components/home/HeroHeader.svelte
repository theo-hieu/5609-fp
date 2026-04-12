<script lang="ts">
  import type { SceneCopy } from '$lib/types';

  export let activeSceneCopy: SceneCopy;
  export let headlineSeason: string;
  export let shotOutcomeLabel: string;
</script>

<header class="border-b border-white/10 bg-slate-950/75 backdrop-blur">
  <div class="mx-auto max-w-7xl px-6 py-10 sm:py-14">
    <p class="text-xs font-semibold uppercase tracking-[0.32em] text-amber-300/80">NBA Shot Evolution</p>
    <div class="mt-4 grid gap-8 lg:grid-cols-[minmax(0,1.6fr)_minmax(18rem,0.9fr)] lg:items-end">
      <div class="max-w-4xl">
        <h1 class="text-4xl font-black tracking-tight text-white sm:text-5xl lg:text-6xl">
          Modern shot selection is a story about math, space, and the shape of the floor.
        </h1>
        <p class="mt-5 max-w-3xl text-sm leading-7 text-slate-300 sm:text-base">
          Scroll through three scenes to see why offenses abandoned the mid-range, why the arc became a weapon,
          and why the corners of the court matter more than their small footprint suggests.
        </p>
      </div>

      <div class="panel p-5">
        <p class="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">Current View</p>
        <div class="mt-4 space-y-3 text-sm text-slate-300">
          <div class="flex items-center justify-between gap-4">
            <span class="text-slate-400">Scene</span>
            <span class="font-semibold text-white">{activeSceneCopy.eyebrow}: {activeSceneCopy.title}</span>
          </div>
          <div class="flex items-center justify-between gap-4">
            <span class="text-slate-400">Season</span>
            <span class="font-semibold text-white">{headlineSeason}</span>
          </div>
          <div class="flex items-center justify-between gap-4">
            <span class="text-slate-400">Shot Lens</span>
            <span class="font-semibold text-white">{shotOutcomeLabel}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</header>
