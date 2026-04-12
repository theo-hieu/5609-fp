<script lang="ts">
  import CourtHeatmap from '$lib/components/CourtHeatmap.svelte';
  import DistanceChart from '$lib/components/DistanceChart.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import type {
    DistanceBucket,
    DistancePayload,
    FilterState,
    HeatmapCell,
    HeatmapPayload,
    SceneCopy,
    SceneId,
    ShotOutcome
  } from '$lib/types';

  export let seasons: string[] = [];
  export let filter: FilterState;
  export let activeScene: SceneId;
  export let activeSceneCopy: SceneCopy;
  export let heatmap: HeatmapPayload | null = null;
  export let distance: DistancePayload | null = null;
  export let onFilterChange: (nextFilter: FilterState) => void;

  $: effectiveShotOutcome =
    activeScene === 3 ? 'made' : activeScene === 2 ? 'all' : filter.shotOutcome;
  $: displayedFilter = { ...filter, shotOutcome: effectiveShotOutcome };
  $: headlineSeason = filter.season === 'all' ? 'All Seasons' : filter.season;
  $: shotOutcomeLabel =
    effectiveShotOutcome === 'all'
      ? 'All shots'
      : effectiveShotOutcome === 'made'
        ? 'Made shots'
        : 'Missed shots';
  $: featuredCardClass = [
    'panel flex flex-col overflow-hidden border transition-all duration-500',
    activeScene === 1
      ? 'border-amber-300/40 bg-slate-900/95 shadow-2xl shadow-amber-950/20'
      : 'border-teal-300/30 bg-slate-900/95 shadow-2xl shadow-teal-950/20'
  ].join(' ');
  $: featuredPanelTitle = activeScene === 1 ? 'Distance Profile' : 'Court Heatmap';
  $: featuredPanelHeading =
    activeScene === 1
      ? 'Volume and efficiency by distance'
      : 'Where log-scaled shot density lives on the floor';
  $: featuredPanelDescription =
    activeScene === 1
      ? 'Scene 1 gives this chart the spotlight so the tradeoff between accuracy and shot value is easier to see.'
      : "Scenes 2 and 3 use a log color scale so the rim's massive shot volume does not drown out the arc, corners, and quieter mid-range pockets.";
  $: selectedHeatmap = selectCollection<HeatmapCell>(heatmap, filter.season);
  $: selectedDistance = selectCollection<DistanceBucket>(distance, filter.season);

  const visibleVisualizationClass =
    'col-start-1 row-start-1 h-full min-h-0 opacity-100 transition-opacity duration-300';
  const hiddenVisualizationClass =
    'col-start-1 row-start-1 h-full min-h-0 opacity-0 pointer-events-none transition-opacity duration-300';

  function selectCollection<T>(collection: { all: T[]; bySeason: Record<string, T[]> } | null, season: string): T[] {
    if (!collection) return [];
    if (season === 'all') return collection.all;
    return collection.bySeason[season] ?? [];
  }

  function handleFilterChange(event: CustomEvent<FilterState>) {
    onFilterChange(event.detail);
  }
</script>

<aside class="lg:sticky lg:top-6 lg:self-start">
  <div class="flex min-h-0 flex-col gap-4 py-8 lg:max-h-[calc(100vh-3rem)] lg:overflow-y-auto lg:pr-2 lg:py-6">
    <section class="panel p-5">
      <FilterBar seasons={seasons} filter={displayedFilter} on:change={handleFilterChange} />
      <p class="mt-4 text-xs leading-6 text-slate-400">
        Scene 2 automatically shows all shot attempts to reveal overall volume. Scene 3 switches to made shots, and
        both heatmap views use a log color scale so the basket area does not wash out the rest of the floor.
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

    <div class="flex flex-col">
      <article class={featuredCardClass}>
        <div class="border-b border-white/10 px-5 py-4">
          <p class="panel-title">{featuredPanelTitle}</p>
          <h3 class="mt-2 text-xl font-bold text-white">{featuredPanelHeading}</h3>
          <p class="mt-2 text-sm leading-6 text-slate-400">{featuredPanelDescription}</p>
        </div>
        <div class="min-h-[24rem] p-5 lg:min-h-[34rem]">
          <div class="grid h-full min-h-0 w-full">
            <div class={activeScene === 1 ? visibleVisualizationClass : hiddenVisualizationClass}>
              <DistanceChart
                data={selectedDistance}
                shotOutcome={effectiveShotOutcome as ShotOutcome}
                longDistanceBucket={distance?.metadata.longDistanceBucket ?? 40}
              />
            </div>

            <div class={activeScene === 1 ? hiddenVisualizationClass : visibleVisualizationClass}>
              <CourtHeatmap
                cells={selectedHeatmap}
                shotOutcome={effectiveShotOutcome as ShotOutcome}
                cellSize={heatmap?.metadata.cellSize ?? 2}
                halfCourtLength={heatmap?.metadata.halfCourtLength ?? 47}
                halfCourtWidth={heatmap?.metadata.halfCourtWidth ?? 25}
              />
            </div>
          </div>
        </div>
      </article>
    </div>
  </div>
</aside>
