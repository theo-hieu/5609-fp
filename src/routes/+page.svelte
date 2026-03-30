<script lang="ts">
  import CourtHeatmap from '$lib/components/CourtHeatmap.svelte';
  import DistanceChart from '$lib/components/DistanceChart.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import PlayerDistanceChart from '$lib/components/PlayerDistanceChart.svelte';
  import SeasonDistanceChart from '$lib/components/SeasonDistanceChart.svelte';
  import ShotTimeline3D from '$lib/components/ShotTimeline3D.svelte';
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
  let seasonDistanceOutcome: ShotOutcome = 'all';
  let playerDistanceOutcome: ShotOutcome = 'all';
  let selectedPlayer = 'LeBron James';
  let shot3dSeason = 'all';
  let shot3dPlayer = 'LeBron James';
  let shot3dOutcome: ShotOutcome = 'made';
  let shot3dProfileMode: 'league' | 'player' = 'league';
  let shot3dPlaying = true;
  let shot3dSpeed = 1;

  $: effectiveShotOutcome =
    activeScene === 3 ? 'made' : activeScene === 2 ? 'all' : filter.shotOutcome;
  $: displayedFilter = { ...filter, shotOutcome: effectiveShotOutcome };
  $: activeSceneCopy = scenes.find((scene) => scene.id === activeScene) ?? scenes[0];
  $: selectedHeatmap = selectCollection<HeatmapCell>(data.heatmap, filter.season);
  $: selectedDistance = selectCollection<DistanceBucket>(data.distance, filter.season);
  $: seasonDistanceLabel =
    seasonDistanceOutcome === 'made'
      ? 'Made shots'
      : seasonDistanceOutcome === 'missed'
        ? 'Missed shots'
        : 'All shots';
  $: seasonDistanceStatLabel =
    seasonDistanceOutcome === 'made'
      ? 'Made-shot distance'
      : seasonDistanceOutcome === 'missed'
        ? 'Missed-shot distance'
        : 'Average distance';
  $: seasonDistancePeak = (data.seasonDistance?.all ?? []).reduce(
    (best, row) => {
      const value =
        seasonDistanceOutcome === 'made'
          ? row.avgMadeShotDistance
          : seasonDistanceOutcome === 'missed'
            ? row.avgMissedShotDistance
            : row.avgShotDistance;
      return !best || value > best.value ? { season: row.season, value } : best;
    },
    null as { season: string; value: number } | null
  );
  $: playerDistanceLabel =
    playerDistanceOutcome === 'made'
      ? 'Made shots'
      : playerDistanceOutcome === 'missed'
        ? 'Missed shots'
        : 'All shots';
  $: playerDistanceStatLabel =
    playerDistanceOutcome === 'made'
      ? 'Made-shot distance'
      : playerDistanceOutcome === 'missed'
        ? 'Missed-shot distance'
        : 'Average distance';
  $: availablePlayers = data.playerDistance?.players ?? [];
  $: if (!shot3dPlayer && availablePlayers.length) {
    shot3dPlayer = availablePlayers[0].player;
  }
  $: if (availablePlayers.length && !availablePlayers.some((player) => player.player === selectedPlayer)) {
    selectedPlayer = availablePlayers[0].player;
  }
  $: selectedPlayerSeries = availablePlayers.find((player) => player.player === selectedPlayer) ?? null;
  $: shot3dPlayerSeasonOptions = (() => {
    const playerSeries = availablePlayers.find((player) => player.player === shot3dPlayer);
    if (!playerSeries) return data.seasons;
    const seasonsSet = new Set(playerSeries.seasons.map((entry) => entry.season));
    return data.seasons.filter((season) => seasonsSet.has(season));
  })();
  $: shot3dPlayerCandidates = availablePlayers.filter(
    (player) => shot3dSeason === 'all' || player.seasons.some((entry) => entry.season === shot3dSeason)
  );
  $: if (shot3dPlayerCandidates.length && !shot3dPlayerCandidates.some((player) => player.player === shot3dPlayer)) {
    shot3dPlayer = shot3dPlayerCandidates[0].player;
  }
  $: shot3dPlayerSeries = availablePlayers.find((player) => player.player === shot3dPlayer) ?? null;
  $: selectedPlayerDistanceTarget = (() => {
    if (!shot3dPlayerSeries) return null;

    if (shot3dSeason !== 'all') {
      const matchingSeason = shot3dPlayerSeries.seasons.find((entry) => entry.season === shot3dSeason);
      return matchingSeason?.avgShotDistance ?? null;
    }

    if (!shot3dPlayerSeries.seasons.length) return null;
    const averageAcrossSeasons =
      shot3dPlayerSeries.seasons.reduce((sum, season) => sum + season.avgShotDistance, 0) /
      shot3dPlayerSeries.seasons.length;
    return +averageAcrossSeasons.toFixed(2);
  })();
  $: selectedPlayerPeak = (selectedPlayerSeries?.seasons ?? []).reduce(
    (best, row) => {
      const value =
        playerDistanceOutcome === 'made'
          ? row.avgMadeShotDistance
          : playerDistanceOutcome === 'missed'
            ? row.avgMissedShotDistance
            : row.avgShotDistance;
      return !best || value > best.value ? { season: row.season, value } : best;
    },
    null as { season: string; value: number } | null
  );
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

  function seasonsForPlayer(playerName: string): string[] {
    const series = availablePlayers.find((player) => player.player === playerName);
    if (!series) return [];
    const seasonSet = new Set(series.seasons.map((entry) => entry.season));
    return data.seasons.filter((season) => seasonSet.has(season));
  }

  function handleShot3dSeasonChange(event: Event) {
    const season = (event.currentTarget as HTMLSelectElement).value;
    shot3dSeason = season;

    const candidates = availablePlayers.filter(
      (player) => season === 'all' || player.seasons.some((entry) => entry.season === season)
    );

    if (candidates.length && !candidates.some((player) => player.player === shot3dPlayer)) {
      shot3dPlayer = candidates[0].player;
    }
  }

  function handleShot3dPlayerChange(event: Event) {
    const player = (event.currentTarget as HTMLSelectElement).value;
    shot3dPlayer = player;

    const seasons = seasonsForPlayer(player);
    if (shot3dSeason !== 'all' && !seasons.includes(shot3dSeason)) {
      shot3dSeason = 'all';
    }
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

        <aside class="lg:sticky lg:top-6 lg:self-start">
          <div class="flex min-h-0 flex-col gap-4 py-8 lg:max-h-[calc(100vh-3rem)] lg:overflow-y-auto lg:pr-2 lg:py-6">
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

      <section class="mt-10">
        <article class="panel overflow-hidden border border-amber-300/20 bg-slate-900/90">
          <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1.9fr)] lg:px-8">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300/80">Season Trend</p>
              <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Average shot distance over time.</h2>
              <p class="mt-4 text-sm leading-7 text-slate-300">
                This view summarizes every season with one number: the average distance, in feet, of all recorded shots.
                As teams leaned harder into spacing and 3-point volume, that average moved farther from the basket.
              </p>
              <div class="mt-5 inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
                {#each [
                  { value: 'all', label: 'All Shots' },
                  { value: 'made', label: 'Made' },
                  { value: 'missed', label: 'Missed' }
                ] as option}
                  <button
                    type="button"
                    class:selected={seasonDistanceOutcome === option.value}
                    class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
                    on:click={() => (seasonDistanceOutcome = option.value as ShotOutcome)}
                  >
                    {option.label}
                  </button>
                {/each}
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Lens</p>
                <p class="mt-2 text-2xl font-bold text-white">{seasonDistanceLabel}</p>
                <p class="mt-1 text-sm text-slate-400">Comparing the same seasons through a different shot outcome filter</p>
              </div>

              <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Peak Season</p>
                <p class="mt-2 text-2xl font-bold text-white">{seasonDistancePeak?.season ?? 'N/A'}</p>
                <p class="mt-1 text-sm text-slate-400">
                  {seasonDistancePeak ? `${seasonDistanceStatLabel}: ${seasonDistancePeak.value.toFixed(2)} ft` : 'No season trend data available'}
                </p>
              </div>
            </div>
          </div>

          <div class="px-6 py-6 lg:px-8">
            <SeasonDistanceChart data={data.seasonDistance?.all ?? []} shotOutcome={seasonDistanceOutcome} />
          </div>
        </article>
      </section>

      <section class="mt-10">
        <article class="panel overflow-hidden border border-teal-300/20 bg-slate-900/90">
          <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1.85fr)] lg:px-8">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/80">Player Focus</p>
              <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">How star players'shot profiles drifted over their careers.</h2>
              <p class="mt-4 text-sm leading-7 text-slate-300">
                Choose one featured player at a time to trace how their shot profile changed across seasons. The chart
                starts at that player&apos;s first shot attempt in the dataset and tracks the average distance of their shots throughout the years.
              </p>
              <div class="mt-5 flex flex-col gap-4 sm:flex-row sm:items-center">
                <label class="flex items-center gap-3 text-sm text-slate-300">
                  <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Player</span>
                  <select
                    class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-teal-400/60"
                    bind:value={selectedPlayer}
                  >
                    {#each availablePlayers as player}
                      <option value={player.player}>{player.player}</option>
                    {/each}
                  </select>
                </label>

                <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
                  {#each [
                    { value: 'all', label: 'All Shots' },
                    { value: 'made', label: 'Made' },
                    { value: 'missed', label: 'Missed' }
                  ] as option}
                    <button
                      type="button"
                      class:selected={playerDistanceOutcome === option.value}
                      class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
                      on:click={() => (playerDistanceOutcome = option.value as ShotOutcome)}
                    >
                      {option.label}
                    </button>
                  {/each}
                </div>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Selected Player</p>
                <p class="mt-2 text-2xl font-bold text-white">{selectedPlayerSeries?.player ?? 'N/A'}</p>
                <p class="mt-1 text-sm text-slate-400">{playerDistanceLabel} view across this player&apos;s career arc</p>
              </div>

              <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Career Window</p>
                <p class="mt-2 text-2xl font-bold text-white">{selectedPlayerSeries?.firstSeason ?? 'N/A'}</p>
                <p class="mt-1 text-sm text-slate-400">
                  {selectedPlayerPeak
                    ? `Peak ${playerDistanceStatLabel.toLowerCase()}: ${selectedPlayerPeak.value.toFixed(2)} ft in ${selectedPlayerPeak.season}`
                    : 'No player trend data available'}
                </p>
              </div>
            </div>
          </div>

          <div class="border-b border-white/10 px-6 py-4 text-sm text-slate-400 lg:px-8">
            Hover any point to compare {playerDistanceStatLabel.toLowerCase()} and shot volume for the selected player-season.
          </div>

          <div class="px-6 py-6 lg:px-8">
            <PlayerDistanceChart player={selectedPlayerSeries} shotOutcome={playerDistanceOutcome} />
          </div>
        </article>
      </section>

      <section class="mt-10">
        <article class="panel overflow-hidden border border-indigo-300/20 bg-slate-900/90">
          <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1.9fr)] lg:px-8">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-indigo-300/80">3D Shot Timeline</p>
              <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Animate shot paths through the season.</h2>
              <p class="mt-4 text-sm leading-7 text-slate-300">
                Watch shots arc toward the rim from a 3D half-court view. Select one season to focus, or leave it on all
                seasons to auto-play through the timeline. Enable player profile mode to approximate that player&apos;s shot
                distance tendencies using the available season-level distance data.
              </p>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <label class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4 text-sm text-slate-300">
                <span class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Season</span>
                <select
                  class="mt-2 w-full rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-indigo-400/60"
                  value={shot3dSeason}
                  on:change={handleShot3dSeasonChange}
                >
                  <option value="all">All seasons (timeline)</option>
                  {#each shot3dPlayerSeasonOptions as season}
                    <option value={season}>{season}</option>
                  {/each}
                </select>
              </label>

              <label class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4 text-sm text-slate-300">
                <span class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Player profile</span>
                <select
                  class="mt-2 w-full rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-indigo-400/60"
                  value={shot3dPlayer}
                  on:change={handleShot3dPlayerChange}
                >
                  {#each shot3dPlayerCandidates as player}
                    <option value={player.player}>{player.player}</option>
                  {/each}
                </select>
              </label>
            </div>
          </div>

          <div class="border-b border-white/10 px-6 py-4 lg:px-8">
            <div class="flex flex-wrap items-center gap-3 text-sm">
              <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
                {#each [
                  { value: 'all', label: 'All Shots' },
                  { value: 'made', label: 'Made' },
                  { value: 'missed', label: 'Missed' }
                ] as option}
                  <button
                    type="button"
                    class:selected={shot3dOutcome === option.value}
                    class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
                    on:click={() => (shot3dOutcome = option.value as ShotOutcome)}
                  >
                    {option.label}
                  </button>
                {/each}
              </div>

              <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
                {#each [
                  { value: 'league', label: 'League Mix' },
                  { value: 'player', label: 'Player Weighted' }
                ] as option}
                  <button
                    type="button"
                    class:selected={shot3dProfileMode === option.value}
                    class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
                    on:click={() => (shot3dProfileMode = option.value as 'league' | 'player')}
                    disabled={option.value === 'player' && !selectedPlayerDistanceTarget}
                  >
                    {option.label}
                  </button>
                {/each}
              </div>

              <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
                <button
                  type="button"
                  class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
                  on:click={() => (shot3dPlaying = !shot3dPlaying)}
                >
                  {shot3dPlaying ? 'Pause' : 'Play'}
                </button>
              </div>

              <div class="inline-flex rounded-2xl border border-white/10 bg-slate-950/90 p-1">
                {#each [0.75, 1, 1.5] as playbackRate}
                  <button
                    type="button"
                    class:selected={shot3dSpeed === playbackRate}
                    class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
                    on:click={() => (shot3dSpeed = playbackRate)}
                  >
                    {playbackRate}x
                  </button>
                {/each}
              </div>
            </div>
          </div>

          <div class="px-6 py-6 lg:px-8">
            <ShotTimeline3D
              heatmap={data.heatmap}
              seasons={data.seasons}
              selectedSeason={shot3dSeason}
              shotOutcome={shot3dOutcome}
              profileMode={shot3dProfileMode}
              playerTargetDistance={selectedPlayerDistanceTarget}
              speed={shot3dSpeed}
              playing={shot3dPlaying}
            />
          </div>
        </article>
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

<style>
  button.selected {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.95), rgba(249, 115, 22, 0.85));
    color: #020617;
  }
</style>
