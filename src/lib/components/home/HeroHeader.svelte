<script lang="ts">
  import type { SceneCopy } from '$lib/types';

  export let activeSceneCopy: SceneCopy;
  export let headlineSeason: string;
  export let shotOutcomeLabel: string;
</script>

<header class="border-b border-white/10 bg-slate-950/75 backdrop-blur">
  <div class="mx-auto max-w-7xl px-6 py-6 sm:py-8 lg:py-10">
    <div class="panel mb-5 border border-white/10 bg-slate-900/70 px-6 py-6 sm:px-8">
      <h1 class="text-3xl font-black tracking-tight text-white sm:text-4xl lg:text-[2.8rem]">
        NBA Shot Evolution: How the League Rewired Shot Selection
      </h1>
      <p class="mt-4 max-w-4xl text-sm leading-7 text-slate-300 sm:text-base">
        This project explores how shot behavior changed from 2003-04 through 2023-24 using millions of tracked attempts,
        combining interactive visuals with scrollytelling to explain the shift from mid-range volume to rim pressure and
        three-point spacing.
      </p>
      <p class="mt-2 max-w-4xl text-xs italic leading-5 text-slate-400">
        Note: Data from the 2020-21 season may show irregular patterns due to the COVID-19 pandemic and schedule disruption.
      </p>
    </div>
  </div>
</header>
