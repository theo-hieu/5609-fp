<script lang="ts">
  import HeroHeader from '$lib/components/home/HeroHeader.svelte';
  import PipelineNotice from '$lib/components/home/PipelineNotice.svelte';
  import StoryGuide from '$lib/components/home/StoryGuide.svelte';
  import StorySidebar from '$lib/components/home/StorySidebar.svelte';
  import CourtHeatmap from '$lib/components/CourtHeatmap.svelte';
  import DistanceChart from '$lib/components/DistanceChart.svelte';
  import FilterBar from '$lib/components/FilterBar.svelte';
  import PlayerDistanceChart from '$lib/components/PlayerDistanceChart.svelte';
  import Scroll from '$lib/components/Scroll.svelte';
  import SeasonDistanceChart from '$lib/components/SeasonDistanceChart.svelte';
  import ShotTimeline3D from '$lib/components/ShotTimeline3D.svelte';
  import ShotTypeTrendChart from '$lib/components/ShotTypeTrendChart.svelte';
  import ZoneTrendChart from '$lib/components/ZoneTrendChart.svelte';
  import type { DistanceBucket, FilterState, HeatmapCell, SceneCopy, SceneId, SeasonDistanceTrend, ShotOutcome } from '$lib/types';
  import type { PageData } from './$types';

  export let data: PageData;

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

  type SeasonHighlight = {
    season: string;
    title: string;
    detail: string;
  };

  const seasonHighlights: SeasonHighlight[] = [
    {
      season: '2003-04',
      title: 'LeBron enters the league',
      detail: 'LeBron James debuts and marks the start of a new high-usage wing era.'
    },
    {
      season: '2004-05',
      title: 'Hand-check era fades',
      detail: 'Perimeter freedom rules reduce hand-checking and gradually open drive-and-kick offense.'
    },
    {
      season: '2009-10',
      title: 'Curry joins the NBA',
      detail: 'Stephen Curry arrives and accelerates the long-term jump in three-point volume.'
    },
    {
      season: '2010-11',
      title: 'LeBron forms Miami Big 3',
      detail: 'LeBron teams with Wade and Bosh, amplifying spread lineups and pace in contender offenses.'
    },
    {
      season: '2014-15',
      title: 'Warriors spacing blueprint',
      detail: 'Golden State wins with pace, spacing, and heavy three-point usage at title level.'
    },
    {
      season: '2015-16',
      title: 'Curry MVP shooting peak',
      detail: 'An all-time high-volume shooting season normalizes deep pull-ups and early-clock threes.'
    },
    {
      season: '2018-19',
      title: 'Freedom-of-movement emphasis',
      detail: 'Rule enforcement on off-ball contact further helps shooters and spacing actions.'
    },
    {
      season: '2020-21',
      title: 'Post-bubble pace and space',
      detail: 'Teams lean further into perimeter-heavy offense after the bubble and short offseason cycles.'
    }
  ];

  let filter: FilterState = { shotOutcome: 'all', season: 'all' };
  let activeScene: SceneId = 1;
  let seasonDistanceOutcome: ShotOutcome = 'all';
  let seasonScrollProgress = 0;
  let shotTypeScrollProgress = 0;
  let zoneScrollProgress = 0;
  let playerScrollProgress = 0;
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
  $: seasonTrendRows = data.seasonDistance?.all ?? [];
  $: clampedSeasonScrollProgress = Math.max(0, Math.min(seasonScrollProgress, 100));
  $: seasonRevealIndex =
    seasonTrendRows.length > 1
      ? Math.round((clampedSeasonScrollProgress / 100) * (seasonTrendRows.length - 1))
      : 0;
  $: activeSeasonTrend = seasonTrendRows[Math.max(0, Math.min(seasonRevealIndex, seasonTrendRows.length - 1))] ?? null;
  $: activeSeason = activeSeasonTrend?.season ?? null;
  $: activeSeasonValue = activeSeasonTrend ? seasonDistanceValue(activeSeasonTrend) : null;
  $: seasonHighlightsWithIndex = seasonHighlights
    .map((highlight) => ({
      ...highlight,
      index: seasonTrendRows.findIndex((row) => row.season === highlight.season)
    }))
    .filter((highlight) => highlight.index >= 0)
    .sort((a, b) => a.index - b.index);
  $: currentHighlight = (() => {
    if (!seasonHighlightsWithIndex.length) return null;
    if (!activeSeasonTrend) return seasonHighlightsWithIndex[0];

    const activeIndex = seasonTrendRows.findIndex((row) => row.season === activeSeasonTrend.season);
    const matchingHighlight = seasonHighlightsWithIndex.filter((highlight) => highlight.index <= activeIndex).at(-1);

    return matchingHighlight ?? seasonHighlightsWithIndex[0];
  })();
  $: seasonStorySteps = seasonTrendRows.map((row, index) => {
    const previous = seasonTrendRows[index - 1] ?? null;
    const value = seasonDistanceValue(row);
    const previousValue = previous ? seasonDistanceValue(previous) : null;
    const delta = previousValue === null ? null : +(value - previousValue).toFixed(2);
    const highlight = seasonHighlights.find((item) => item.season === row.season) ?? null;

    return {
      season: row.season,
      value,
      delta,
      highlight,
      attempts: row.attempts
    };
  });
  $: shotTypeFirstSeason = data.shotTypeTrend?.all[0] ?? null;
  $: shotTypeLastSeason = data.shotTypeTrend?.all[data.shotTypeTrend.all.length - 1] ?? null;
  $: twoPointFirstShare = shotTypeFirstSeason?.shotTypes.find((entry) => entry.shotType === '2PT Field Goal')?.share ?? 0;
  $: threePointFirstShare = shotTypeFirstSeason?.shotTypes.find((entry) => entry.shotType === '3PT Field Goal')?.share ?? 0;
  $: twoPointLastShare = shotTypeLastSeason?.shotTypes.find((entry) => entry.shotType === '2PT Field Goal')?.share ?? 0;
  $: threePointLastShare = shotTypeLastSeason?.shotTypes.find((entry) => entry.shotType === '3PT Field Goal')?.share ?? 0;
  $: zoneFirstSeason = data.zoneTrend?.all[0] ?? null;
  $: zoneLastSeason = data.zoneTrend?.all[data.zoneTrend.all.length - 1] ?? null;
  $: aboveBreakFirstShare = zoneFirstSeason?.zones.find((entry) => entry.zone === 'Above the Break 3')?.share ?? 0;
  $: aboveBreakLastShare = zoneLastSeason?.zones.find((entry) => entry.zone === 'Above the Break 3')?.share ?? 0;
  $: midRangeFirstShare = zoneFirstSeason?.zones.find((entry) => entry.zone === 'Mid-Range')?.share ?? 0;
  $: midRangeLastShare = zoneLastSeason?.zones.find((entry) => entry.zone === 'Mid-Range')?.share ?? 0;
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

  function handleFilterChange(nextFilter: FilterState) {
    filter = nextFilter;
  }

  function seasonDistanceValue(row: SeasonDistanceTrend) {
    if (seasonDistanceOutcome === 'made') return row.avgMadeShotDistance;
    if (seasonDistanceOutcome === 'missed') return row.avgMissedShotDistance;
    return row.avgShotDistance;
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

  function trackPlayerScroll(node: HTMLElement) {
    const clamp = (min: number, value: number, max: number) => Math.min(Math.max(value, min), max);

    const updateProgress = () => {
      const rect = node.getBoundingClientRect();
      const viewportHeight = window.innerHeight;
      const start = viewportHeight * 0.74;
      const end = viewportHeight * 0.18;
      const revealWindow = rect.height * 0.68;
      const denominator = Math.max(revealWindow + start - end, 1);
      const nextProgress = ((start - rect.top) / denominator) * 100;
      playerScrollProgress = clamp(0, nextProgress, 100);
    };

    updateProgress();
    window.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress);

    const resizeObserver = new ResizeObserver(updateProgress);
    resizeObserver.observe(node);

    return {
      destroy() {
        window.removeEventListener('scroll', updateProgress);
        window.removeEventListener('resize', updateProgress);
        resizeObserver.disconnect();
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
      <div class="flex flex-col">
      <section class="order-4 grid gap-10 lg:grid-cols-[minmax(0,2fr)_minmax(0,3fr)] lg:items-start">
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

      <section class="order-1 mt-10">
        <Scroll
          bind:progress={seasonScrollProgress}
          threshold={0.64}
          margin={8}
          storyWidth="minmax(0, 0.75fr)"
          vizWidth="minmax(0, 1.55fr)"
          gap="2rem"
        >
          {#snippet children()}
            <div class="space-y-6">
              <article class="panel border border-amber-300/20 bg-slate-900/90 p-5 sm:p-6">
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300/80">Season Trend</p>
                <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Average shot distance over time.</h2>
                <p class="mt-4 text-sm leading-7 text-slate-300">
                  Scroll to move season-by-season through the timeline. The line reveals as you scroll, and the highlight
                  cards follow key moments like LeBron&apos;s debut, Curry&apos;s arrival, and major rule emphasis changes.
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

                <div class="mt-5 grid gap-4 sm:grid-cols-2">
                  <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Lens</p>
                    <p class="mt-2 text-2xl font-bold text-white">{seasonDistanceLabel}</p>
                    <p class="mt-1 text-sm text-slate-400">Current season: {activeSeason ?? 'N/A'}</p>
                    <p class="mt-1 text-sm text-slate-400">
                      {activeSeasonValue !== null ? `${activeSeasonValue.toFixed(2)} ft` : 'No season trend data available'}
                    </p>
                  </div>

                  <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Current Highlight</p>
                    <p class="mt-2 text-2xl font-bold text-white">{currentHighlight?.season ?? 'N/A'}</p>
                    <p class="mt-1 text-sm font-semibold text-amber-200">{currentHighlight?.title ?? 'No highlight mapped yet'}</p>
                    <p class="mt-1 text-sm text-slate-400">{currentHighlight?.detail ?? 'Add a highlight event for this era.'}</p>
                  </div>
                </div>
              </article>

              {#each seasonStorySteps as step}
                <article
                  class={`panel min-h-[38vh] border bg-slate-900/85 p-5 sm:p-6 ${step.highlight ? 'border-amber-300/30' : 'border-white/10'}`}
                >
                  <p class="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300/80">Season {step.season}</p>
                  <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">
                    {step.value.toFixed(2)} ft average distance
                  </h2>
                  <p class="mt-3 text-sm leading-7 text-slate-300">
                    {#if step.delta === null}
                      Starting point for this timeline in the current {seasonDistanceLabel.toLowerCase()} lens.
                    {:else if step.delta >= 0}
                      Up {step.delta.toFixed(2)} ft from the previous season as teams continue stretching the floor.
                    {:else}
                      Down {Math.abs(step.delta).toFixed(2)} ft from the previous season, a temporary pause in the long-range trend.
                    {/if}
                  </p>
                  <p class="mt-2 text-sm text-slate-400">Attempts: {step.attempts.toLocaleString()}</p>

                  {#if step.highlight}
                    <div class="mt-4 rounded-2xl border border-amber-300/25 bg-amber-400/10 px-4 py-3">
                      <p class="text-xs font-semibold uppercase tracking-[0.18em] text-amber-200">League Highlight</p>
                      <p class="mt-1 text-base font-semibold text-amber-100">{step.highlight.title}</p>
                      <p class="mt-1 text-sm leading-6 text-amber-50/90">{step.highlight.detail}</p>
                    </div>
                  {/if}
                </article>
              {/each}
            </div>
          {/snippet}

          {#snippet viz()}
            <article class="panel overflow-hidden border border-amber-300/20 bg-slate-900/90">
              <div class="px-6 py-6 lg:px-8">
                <SeasonDistanceChart
                  data={seasonTrendRows}
                  shotOutcome={seasonDistanceOutcome}
                  revealProgress={seasonScrollProgress}
                />
              </div>
            </article>
          {/snippet}
        </Scroll>
      </section>

      <section class="order-2 mt-10">
        <Scroll bind:progress={shotTypeScrollProgress} threshold={0.72} margin={8}>
          {#snippet children()}
            <div>
              <article class="panel min-h-[120vh] border border-cyan-300/20 bg-slate-900/90 p-6 sm:p-8">
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300/80">Evidence 1</p>
                <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">The rise in distance is really a rise in 3-point share.</h2>
                <p class="mt-4 text-sm leading-7 text-slate-300">
                  Average distance alone is only a clue, not proof. Maybe the league is just taking more long twos instead of threes. 
                  To confirm the story, we need to see the shot type mix shift in favor of threes over time. Scroll to see how 2pt and 3pt share evolve over time.
                </p>

                <div class="mt-8 grid gap-4 sm:grid-cols-2">
                  <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">3PT Share Change</p>
                    <p class="mt-2 text-2xl font-bold text-white">
                      {shotTypeLastSeason ? `${(threePointFirstShare * 100).toFixed(1)}% -> ${(threePointLastShare * 100).toFixed(1)}%` : 'N/A'}
                    </p>
                    <p class="mt-1 text-sm text-slate-400">
                      {shotTypeFirstSeason && shotTypeLastSeason ? `${shotTypeFirstSeason.season} to ${shotTypeLastSeason.season}` : 'No shot type trend data available'}
                    </p>
                  </div>

                  <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">2PT Share Change</p>
                    <p class="mt-2 text-2xl font-bold text-white">
                      {shotTypeLastSeason ? `${(twoPointFirstShare * 100).toFixed(1)}% -> ${(twoPointLastShare * 100).toFixed(1)}%` : 'N/A'}
                    </p>
                    <p class="mt-1 text-sm text-slate-400">The two-point share falls as the three-point line absorbs more attempts</p>
                  </div>
                </div>

                <p class="mt-8 text-sm leading-7 text-slate-300">
                  Together these two lines show that the increase in average distance is not just longer two-pointers.
                  The shot mix itself changes, with threes increasing their share of attempts as the years go on. 
                  This confirms that the distance trend is really about offenses hunting the extra point value that comes with three-pointers, not just taking more long shots in general.
              </article>
            </div>
          {/snippet}

          {#snippet viz()}
            <article class="panel overflow-hidden border border-cyan-300/20 bg-slate-900/90">
              <div class="border-b border-white/10 px-6 py-5 lg:px-8">
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300/80">Evidence 1</p>
                <h3 class="mt-2 text-2xl font-bold text-white">2PT vs 3PT share over time</h3>
              </div>
              <div class="px-6 py-6 lg:px-8">
                <ShotTypeTrendChart data={data.shotTypeTrend?.all ?? []} revealProgress={shotTypeScrollProgress} />
              </div>
            </article>
          {/snippet}
        </Scroll>
      </section>

      <section class="order-3 mt-10">
        <Scroll bind:progress={zoneScrollProgress} threshold={0.72} margin={8}>
          {#snippet children()}
            <div>
              <article class="panel min-h-[120vh] border border-rose-300/20 bg-slate-900/90 p-6 sm:p-8">
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-rose-300/80">Evidence 2</p>
                <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">The spatial shift is concentrated in specific zones.</h2>
                <p class="mt-4 text-sm leading-7 text-slate-300">
                  Teams aren't taking more shots per game, so where are the new threes coming from? 
                  Here is a 7 zone breakdown of shot distribution change over time, showing that the above-the-break 
                  three-point zone increases significantly while the mid-range zone declines sharply. 

                </p>

                <div class="mt-8 grid gap-4 sm:grid-cols-2">
                  <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Above-the-Break 3</p>
                    <p class="mt-2 text-2xl font-bold text-white">
                      {zoneLastSeason ? `${(aboveBreakFirstShare * 100).toFixed(1)}% -> ${(aboveBreakLastShare * 100).toFixed(1)}%` : 'N/A'}
                    </p>
                    <p class="mt-1 text-sm text-slate-400">The zone most closely tied to modern spacing grows sharply over time</p>
                  </div>

                  <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Mid-Range</p>
                    <p class="mt-2 text-2xl font-bold text-white">
                      {zoneLastSeason ? `${(midRangeFirstShare * 100).toFixed(1)}% -> ${(midRangeLastShare * 100).toFixed(1)}%` : 'N/A'}
                    </p>
                    <p class="mt-1 text-sm text-slate-400">Mid-range volume loses share as offenses reallocate attempts</p>
                  </div>
                </div>

                <p class="mt-8 text-sm leading-7 text-slate-300">
                  This is the mechanism behind the broader shot-distance story: mid-range shots are dying as the above-the-break three grows. 
                  Teams are prioritizing long threes over long twos because of the extra point of value, leading to more and more 3 point attempts.
                  They share for restricted area shots(layups and dunks) nearly equal share as above the break three pointers, meaning teams aim for threes
                  or attack the rim, prefering nothing in between.
                </p>
              </article>
            </div>
          {/snippet}

          {#snippet viz()}
            <article class="panel overflow-hidden border border-rose-300/20 bg-slate-900/90">
              <div class="border-b border-white/10 px-6 py-5 lg:px-8">
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-rose-300/80">Evidence 2</p>
                <h3 class="mt-2 text-2xl font-bold text-white">Shot distribution by zone</h3>
              </div>
              <div class="px-6 py-6 lg:px-8">
                <ZoneTrendChart
                  data={data.zoneTrend?.all ?? []}
                  zones={data.zoneTrend?.zones ?? []}
                  revealProgress={zoneScrollProgress}
                />
              </div>
            </article>
          {/snippet}
        </Scroll>
      </section>

      <section class="order-5 relative left-1/2 mt-10 w-screen -translate-x-1/2 px-6 sm:px-8 lg:px-10 xl:px-12">
        <div use:trackPlayerScroll class="mx-auto w-full max-w-[110rem]">
          <div class="lg:sticky lg:top-6">
            <article class="panel w-full overflow-hidden border border-teal-300/20 bg-slate-900/90">
              <div class="grid gap-6 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)] lg:px-8">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/80">Player Focus</p>
                  <h3 class="mt-3 text-2xl font-bold text-white">Player distance trend over time</h3>
                  <p class="mt-3 text-sm leading-6 text-slate-400">
                     Select one of the featured players and scroll to see how their average shot distance changes throughout their career. You can select Lebron for his longevity,
                     Curry and Harden for their 3pt shooting evolution, and Durant for his elite 3 level scoring ability.
                </div>

                <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-end">
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

              <div class="border-b border-white/10 px-6 py-4 text-sm text-slate-400 lg:px-8">
                Hover any point to compare {playerDistanceStatLabel.toLowerCase()} and shot volume for the selected player-season.
              </div>

              <div class="px-4 py-6 sm:px-6 lg:px-8">
                <PlayerDistanceChart
                  player={selectedPlayerSeries}
                  shotOutcome={playerDistanceOutcome}
                  revealProgress={playerScrollProgress}
                />
              </div>
            </article>
          </div>

          <div class="pointer-events-none mt-6 space-y-6 opacity-0">
            <article class="panel min-h-[108vh] border border-teal-300/20 bg-slate-900/90 p-6 sm:p-8">
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/80">Player Focus</p>
              <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">How star players&apos; shot profiles drifted over their careers.</h2>
              <p class="mt-4 text-sm leading-7 text-slate-300">
                Choose one featured player at a time to trace how their shot profile changed across seasons. The chart
                begins at that player&apos;s first shot attempt in the dataset and keeps revealing as the user scrolls.
              </p>
            </article>

            <article class="panel min-h-[108vh] border border-white/10 bg-slate-900/80 p-6 sm:p-8">
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
            </article>
          </div>
        </div>
      </section>

      <section class="order-6 mt-10">
        <article class="panel overflow-hidden border border-indigo-300/25 bg-slate-900/90">
          <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1.85fr)] lg:px-8">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-indigo-200/80">3D Shot Timeline</p>
              <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">See the evolution play out across the floor.</h2>
              <p class="mt-4 text-sm leading-7 text-slate-300">
                This final view is less about proving the claim and more about letting the user feel it spatially. The
                animation pulls all of the earlier trends back onto the court, so you can watch how shot selection shifts
                over time from a full-floor perspective.
              </p>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="rounded-3xl border border-white/10 bg-slate-950/70 px-5 py-5">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Timeline Scope</p>
                <p class="mt-3 text-2xl font-bold text-white">All Seasons</p>
                <p class="mt-2 text-sm leading-6 text-slate-400">
                  The animation plays as one continuous league-wide timeline so the spatial shift is easier to read.
                </p>
              </div>

              <div class="rounded-3xl border border-white/10 bg-slate-950/70 px-5 py-5">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Current Mode</p>
                <p class="mt-3 text-2xl font-bold text-white">League Mix</p>
                <p class="mt-2 text-sm leading-6 text-slate-400">
                  Player and season filters can come back later. For now this view stays focused on the overall shot map.
                </p>
              </div>
            </div>
          </div>

          <div class="p-3 sm:p-4 lg:p-5">
            <ShotTimeline3D
              heatmap={data.heatmap}
              seasons={data.seasons}
              selectedSeason="all"
              shotOutcome="all"
              profileMode="league"
              playerTargetDistance={null}
              speed={1}
              playing={true}
              showControls={false}
            />
          </div>
        </article>
      </section>
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
