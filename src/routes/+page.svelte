<script lang="ts">
  import CoordinatedShotEvolution from '$lib/components/CoordinatedShotEvolution.svelte';
  import DistanceProfileSection from '$lib/components/home/DistanceProfileSection.svelte';
  import ExploreDataSection from '$lib/components/home/ExploreDataSection.svelte';
  import Heatmap3DSection from '$lib/components/home/Heatmap3DSection.svelte';
  import HeatmapComparisonSection from '$lib/components/home/HeatmapComparisonSection.svelte';
  import HeroHeader from '$lib/components/home/HeroHeader.svelte';
  import PipelineNotice from '$lib/components/home/PipelineNotice.svelte';
  import PlayerFocusStickySection from '$lib/components/home/PlayerFocusStickySection.svelte';
  import ShotTimelineShowcaseSection from '$lib/components/home/ShotTimelineShowcaseSection.svelte';
  import { deriveThesisMetrics } from '$lib/content/shotEvolutionStory';
  import type { PageData } from './$types';

  export let data: PageData;

  $: thesisMetrics = deriveThesisMetrics(
    data.seasonDistance?.all ?? [],
    data.shotTypeTrend?.all ?? [],
    data.zoneTrend?.all ?? []
  );
</script>

<svelte:head>
  <title>NBA Shot Evolution Scrollytelling</title>
  <meta
    name="description"
    content="A scrollytelling NBA shot evolution dashboard built with SvelteKit, TailwindCSS, D3, and Chart.js."
  />
</svelte:head>

<div class="min-h-screen overflow-x-clip">
  <HeroHeader metrics={thesisMetrics} />

  <main class="mx-auto max-w-[118rem] px-4 pb-16 sm:px-6 lg:px-8">
    {#if !data.pipelineReady}
      <PipelineNotice />
    {:else}
      <div class="flex flex-col">
        <CoordinatedShotEvolution
          seasonDistance={data.seasonDistance?.all ?? []}
          shotTypeTrend={data.shotTypeTrend?.all ?? []}
          zoneTrend={data.zoneTrend?.all ?? []}
          zones={data.zoneTrend?.zones ?? []}
        />

        <DistanceProfileSection seasons={data.seasons} distance={data.distance} />

        <HeatmapComparisonSection heatmap={data.heatmap} seasons={data.seasons} />

        <Heatmap3DSection heatmap={data.heatmap} seasons={data.seasons} />

        <PlayerFocusStickySection players={data.playerDistance?.players ?? []} />

        <ShotTimelineShowcaseSection
          heatmap={data.heatmap}
          seasons={data.seasons}
          players={data.playerDistance?.players ?? []}
        />

        <ExploreDataSection
          seasons={data.seasons}
          distance={data.distance}
          heatmap={data.heatmap}
          players={data.playerDistance?.players ?? []}
        />
      </div>

      <footer class="pb-4 text-sm text-slate-400">
        Aggregated from Kaggle dataset
        <a
          href="https://www.kaggle.com/datasets/mexwell/nba-shots"
          class="font-semibold text-amber-200 underline decoration-amber-400/40 underline-offset-4"
          target="_blank"
          rel="noreferrer"
        >
          mexwell/nba-shots
        </a>
      </footer>
    {/if}
  </main>
</div>
