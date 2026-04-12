<script lang="ts">
  import HeroHeader from '$lib/components/home/HeroHeader.svelte';
  import PipelineNotice from '$lib/components/home/PipelineNotice.svelte';
  import PlayerFocusSection from '$lib/components/home/PlayerFocusSection.svelte';
  import SeasonTrendSection from '$lib/components/home/SeasonTrendSection.svelte';
  import ShotTimelineSection from '$lib/components/home/ShotTimelineSection.svelte';
  import StoryGuide from '$lib/components/home/StoryGuide.svelte';
  import StorySidebar from '$lib/components/home/StorySidebar.svelte';
  import { scenes } from '$lib/content/scenes';
  import type { FilterState, SceneId } from '$lib/types';
  import type { PageData } from './$types';

  export let data: PageData;

  let filter: FilterState = { shotOutcome: 'all', season: 'all' };
  let activeScene: SceneId = 1;

  $: effectiveShotOutcome =
    activeScene === 3 ? 'made' : activeScene === 2 ? 'all' : filter.shotOutcome;
  $: activeSceneCopy = scenes.find((scene) => scene.id === activeScene) ?? scenes[0];
  $: headlineSeason = filter.season === 'all' ? 'All Seasons' : filter.season;
  $: shotOutcomeLabel =
    effectiveShotOutcome === 'all'
      ? 'All shots'
      : effectiveShotOutcome === 'made'
        ? 'Made shots'
        : 'Missed shots';

  function handleFilterChange(nextFilter: FilterState) {
    filter = nextFilter;
  }

  function observeScene(node: HTMLElement, scene: SceneId) {
    let sceneId = scene;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          activeScene = sceneId;
        }
      },
      {
        rootMargin: '-30% 0px -35% 0px',
        threshold: 0.35
      }
    );

    observer.observe(node);

    return {
      update(nextScene: SceneId) {
        sceneId = nextScene;
      },
      destroy() {
        observer.disconnect();
      }
    };
  }
</script>

<svelte:head>
  <title>NBA Shot Evolution Scrollytelling</title>
  <meta
    name="description"
    content="A scrollytelling NBA shot evolution dashboard built with SvelteKit, TailwindCSS, D3, and Chart.js."
  />
</svelte:head>

<div class="min-h-screen">
  <HeroHeader {activeSceneCopy} {headlineSeason} {shotOutcomeLabel} />

  <main class="mx-auto max-w-7xl px-6 pb-16">
    {#if !data.pipelineReady}
      <PipelineNotice />
    {:else}
      <section class="grid gap-10 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)] lg:items-start">
        <StoryGuide {scenes} {activeScene} {observeScene} />
        <StorySidebar
          seasons={data.seasons}
          {filter}
          {activeScene}
          {activeSceneCopy}
          heatmap={data.heatmap}
          distance={data.distance}
          onFilterChange={handleFilterChange}
        />
      </section>

      <SeasonTrendSection data={data.seasonDistance?.all ?? []} />
      <PlayerFocusSection players={data.playerDistance?.players ?? []} />
      <ShotTimelineSection heatmap={data.heatmap} seasons={data.seasons} players={data.playerDistance?.players ?? []} />

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
        into lightweight JSON files stored at <code>src/lib/data</code>.
      </footer>
    {/if}
  </main>
</div>
