<script lang="ts">
  import CourtHeatmap from '$lib/components/CourtHeatmap.svelte';
  import DistanceChart from '$lib/components/DistanceChart.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import type { DistanceBucket, FilterState, HeatmapCell, ShotOutcome } from '$lib/types';
  import type { PageData } from './$types';

  export let data: PageData;

  type SceneId = 1 | 2 | 3;

  interface SceneCopy {
    id: SceneId;
    eyebrow: string;
    title: string;
    description: string;
    paragraphs: string[];
  }

  const scenes: SceneCopy[] = [
    {
      id: 1,
      eyebrow: 'Scene 1',
      title: 'The Value of Distance',
      description: 'The shot chart starts with a simple truth: distance hurts accuracy, but the 3-point line changes the reward.',
      paragraphs: [
        'Every extra step away from the rim makes the shot a little harder. Finishes in the paint are converted at the highest rates, then efficiency steadily slides as attempts move through the lane, into the floater area, and out toward the long two.',
        'The twist is that the court does not pay every made basket the same way. Once a shooter crosses the 3-point line, the expected value of the attempt jumps from two points to three, and that extra point can outweigh the drop in raw field goal percentage.',
        'That is why the distance profile bends around the arc. Shots from 22 feet and beyond are less accurate than short jumpers, but they can still return more points per attempt, which makes them rational shots for modern offenses to keep hunting.'
      ]
    },
    {
      id: 2,
      eyebrow: 'Scene 2',
      title: 'Hunting High-Value Real Estate',
      description: 'Once teams understand the math, shot selection stops looking balanced and starts looking optimized.',
      paragraphs: [
        'If the rim produces the easiest two points and the arc produces the most valuable jumpers, offenses naturally stop treating the court as evenly useful space. The result is a map with two bright clusters instead of one smooth spread of attempts.',
        'The heatmap shows those two magnets clearly: a dense pocket directly at the basket and a ring of attempts sitting just behind the 3-point line. Those are the places where expected return is strongest, so that is where possessions get concentrated.',
        'Everything in between pays the price. Mid-range shots never disappear completely, but compared with the paint and the arc, that part of the floor becomes noticeably quiet because it offers neither elite accuracy nor elite scoring value.'
      ]
    },
    {
      id: 3,
      eyebrow: 'Scene 3',
      title: 'Court Geography & Zones',
      description: 'Distance alone is not enough. The shape of the line itself creates some of the most efficient shots on the floor.',
      paragraphs: [
        'Not all threes are created equal. The corner 3 is closer to the basket than an above-the-break 3, yet it is still worth the same three points, which means the geometry of the court creates a special shortcut to efficient offense.',
        'That shorter path makes the corner three one of the best non-rim shots in basketball. Outside of dunks, layups, and point-blank finishes, it is often the cleanest combination of manageable distance and maximum reward.',
        'When the view switches to made shots, the most productive zones sharpen immediately. The paint glows because close finishes are efficient, and the corners stand out because spacing the floor there turns court geometry into one of the league\'s most reliable sources of efficient scoring.'
      ]
    }
  ];

  let filter: FilterState = { shotOutcome: 'all', season: 'all' };
  let activeScene: SceneId = 1;

  $: effectiveShotOutcome =
    activeScene === 3 ? 'made' : activeScene === 2 ? 'all' : filter.shotOutcome;
  $: displayedFilter = { ...filter, shotOutcome: effectiveShotOutcome };
  $: activeSceneCopy = scenes.find((scene) => scene.id === activeScene) ?? scenes[0];
  $: selectedHeatmap = selectCollection<HeatmapCell>(data.heatmap, filter.season);
  $: selectedDistance = selectCollection<DistanceBucket>(data.distance, filter.season);
  $: headlineSeason = filter.season === 'all' ? 'All Seasons' : filter.season;
  $: shotOutcomeLabel =
    effectiveShotOutcome === 'all'
      ? 'All shots'
      : effectiveShotOutcome === 'made'
        ? 'Made shots'
        : 'Missed shots';
  $: featuredCardClass = [
    'panel flex min-h-0 flex-col overflow-hidden border transition-all duration-500',
    activeScene === 1
      ? 'border-amber-300/40 bg-slate-900/95 shadow-2xl shadow-amber-950/20'
      : 'border-teal-300/30 bg-slate-900/95 shadow-2xl shadow-teal-950/20'
  ].join(' ');
  $: featuredPanelTitle = activeScene === 1 ? 'Distance Profile' : 'Court Heatmap';
  $: featuredPanelHeading =
    activeScene === 1
      ? 'Volume and efficiency by distance'
      : 'Where shot volume and efficiency live on the floor';
  $: featuredPanelDescription =
    activeScene === 1
      ? 'Scene 1 gives this chart the spotlight so the tradeoff between accuracy and shot value is easier to see.'
      : 'Scenes 2 and 3 shift attention here to compare raw attempt density against made-shot hotspots.';
  $: visibleVisualizationClass = 'col-start-1 row-start-1 h-full min-h-0 opacity-100 transition-opacity duration-300';
  $: hiddenVisualizationClass =
    'col-start-1 row-start-1 h-full min-h-0 opacity-0 pointer-events-none transition-opacity duration-300';

  function selectCollection<T>(collection: { all: T[]; bySeason: Record<string, T[]> } | null, season: string): T[] {
    if (!collection) return [];
    if (season === 'all') return collection.all;
    return collection.bySeason[season] ?? [];
  }

  function handleFilterChange(event: CustomEvent<FilterState>) {
    filter = event.detail;
  }

  function handleSceneChange(event: CustomEvent<SceneId>) {
    activeScene = event.detail;
  }

  function observeScene(node: HTMLElement, scene: SceneId) {
    let sceneId = scene;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          node.dispatchEvent(new CustomEvent<SceneId>('scenechange', { detail: sceneId }));
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

  <main class="mx-auto max-w-7xl px-6 pb-16">
    {#if !data.pipelineReady}
      <section class="panel mt-8 p-8 text-center">
        <h2 class="text-2xl font-bold text-white">Aggregated data has not been generated yet.</h2>
        <p class="mt-3 text-sm text-slate-300">
          Run the local data pipeline to read the raw CSV files in <code>data_raw</code> and build lightweight JSON into
          <code>src/lib/data</code>.
        </p>
        <pre class="mx-auto mt-6 max-w-3xl overflow-x-auto rounded-2xl bg-slate-950/90 p-4 text-left text-sm text-amber-200"><code>python scripts/process_data.py</code></pre>
      </section>
    {:else}
      <section class="grid gap-10 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)] lg:items-start">
        <div class="py-8 lg:py-10">
          <div class="mb-8 max-w-2xl">
            <p class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">Story Guide</p>
            <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Scroll the narrative to steer the dashboard.</h2>
            <p class="mt-4 text-sm leading-7 text-slate-300">
              Each block below activates a new scene. Season stays interactive throughout, while the story shifts the
              shot outcome lens when it needs to emphasize total volume or made-shot efficiency.
            </p>
          </div>

          <div class="space-y-8">
            {#each scenes as scene}
              <article
                use:observeScene={scene.id}
                on:scenechange={handleSceneChange}
                class={[
                  'panel flex min-h-[80vh] flex-col justify-center p-6 transition-all duration-500 sm:p-8',
                  activeScene === scene.id
                    ? 'border-amber-300/40 bg-slate-900/90 shadow-2xl shadow-amber-950/15'
                    : 'border-white/10 bg-slate-900/55'
                ].join(' ')}
              >
                <p class="text-xs font-semibold uppercase tracking-[0.28em] text-amber-300/80">{scene.eyebrow}</p>
                <h3 class="mt-4 text-3xl font-black tracking-tight text-white sm:text-4xl">{scene.title}</h3>
                <p class="mt-4 max-w-2xl text-base leading-7 text-slate-200">{scene.description}</p>

                <div class="mt-8 space-y-5 text-sm leading-7 text-slate-300 sm:text-base">
                  {#each scene.paragraphs as paragraph}
                    <p>{paragraph}</p>
                  {/each}
                </div>
              </article>
            {/each}
          </div>
        </div>

        <aside class="lg:sticky lg:top-0 lg:h-screen lg:overflow-hidden">
          <div class="flex h-full min-h-0 flex-col gap-4 overflow-hidden py-8 lg:py-10">
            <section class="panel p-5">
              <FilterBar seasons={data.seasons} filter={displayedFilter} on:change={handleFilterChange} />
              <p class="mt-4 text-xs leading-6 text-slate-400">
                Scene 2 automatically shows all shot attempts to reveal overall volume. Scene 3 switches to made shots
                so the heatmap highlights efficiency hotspots.
              </p>
            </section>

            <section class="panel p-5">
              <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p class="panel-title">Pinned Visualization Stage</p>
                  <h2 class="mt-2 text-2xl font-bold text-white">{activeSceneCopy.title}</h2>
                </div>
                <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-slate-300">
                  <div class="font-semibold text-white">{shotOutcomeLabel}</div>
                  <div class="mt-1 text-slate-400">{headlineSeason}</div>
                </div>
              </div>
              <p class="mt-4 text-sm leading-6 text-slate-400">{activeSceneCopy.description}</p>
            </section>

            <div class="flex min-h-0 flex-1 flex-col overflow-hidden">
              <article class={featuredCardClass}>
                <div class="border-b border-white/10 px-5 py-4">
                  <p class="panel-title">{featuredPanelTitle}</p>
                  <h3 class="mt-2 text-xl font-bold text-white">{featuredPanelHeading}</h3>
                  <p class="mt-2 text-sm leading-6 text-slate-400">{featuredPanelDescription}</p>
                </div>
                <div class="min-h-[22rem] flex-1 p-5 lg:min-h-0">
                  <div class="grid h-full min-h-0 w-full">
                    <div class={activeScene === 1 ? visibleVisualizationClass : hiddenVisualizationClass}>
                      <DistanceChart
                        data={selectedDistance}
                        shotOutcome={effectiveShotOutcome}
                        longDistanceBucket={data.distance?.metadata.longDistanceBucket ?? 40}
                      />
                    </div>

                    <div class={activeScene === 1 ? hiddenVisualizationClass : visibleVisualizationClass}>
                      <CourtHeatmap
                        cells={selectedHeatmap}
                        shotOutcome={effectiveShotOutcome}
                        cellSize={data.heatmap?.metadata.cellSize ?? 2}
                        halfCourtLength={data.heatmap?.metadata.halfCourtLength ?? 47}
                        halfCourtWidth={data.heatmap?.metadata.halfCourtWidth ?? 25}
                      />
                    </div>
                  </div>
                </div>
              </article>
            </div>
          </div>
        </aside>
      </section>

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
