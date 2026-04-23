<script lang="ts">
  import HeroHeader from '$lib/components/home/HeroHeader.svelte';
  import PipelineNotice from '$lib/components/home/PipelineNotice.svelte';
  import CourtHeatmap from '$lib/components/CourtHeatmap.svelte';
  import CourtHeatmap3D from '$lib/components/CourtHeatmap3D.svelte';
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
  let heatmapTransitionScrollProgress = 0;
  let heatmap3dOutcome: ShotOutcome = 'all';
  let shotTypeScrollProgress = 0;
  let zoneScrollProgress = 0;
  let playerScrollProgress = 0;
  let distanceHighlightActive = false;
  let heatmapSeason = 'all';
  let playerDistanceOutcome: ShotOutcome = 'all';
  let selectedPlayer = 'LeBron James';
  let shot3dSeason = 'all';
  let shot3dPlayer = 'LeBron James';
  let shot3dOutcome: ShotOutcome = 'all';
  let shot3dProfileMode: 'league' | 'player' = 'league';
  let shot3dPlaying = true;
  let shot3dSpeed = 1;
  let shot3dLoop = true;

  $: effectiveShotOutcome =
    activeScene === 3 ? heatmap3dOutcome : activeScene === 2 ? 'all' : filter.shotOutcome;
  $: displayedFilter = { ...filter, shotOutcome: effectiveShotOutcome };
  $: activeSceneCopy = scenes.find((scene) => scene.id === activeScene) ?? scenes[0];
  $: selectedHeatmap = selectCollection<HeatmapCell>(data.heatmap, heatmapSeason);
  $: selectedDistance = selectCollection<DistanceBucket>(data.distance, filter.season);
  $: heatmapSeasonLabel = heatmapSeason === 'all' ? 'All Seasons' : heatmapSeason;
  $: heatmap3dLabel =
    heatmap3dOutcome === 'made'
      ? 'Made shots'
      : heatmap3dOutcome === 'missed'
        ? 'Missed shots'
        : 'All shots';
  $: heatmap3dPeakValue = selectedHeatmap.reduce(
    (best, cell) => Math.max(best, heatmapMetricValue(cell, heatmap3dOutcome)),
    0
  );
  $: heatmap3dActiveBins = selectedHeatmap.filter((cell) => heatmapMetricValue(cell, heatmap3dOutcome) > 0).length;
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
  $: heatmapFadeProgress = Math.max(0, Math.min((heatmapTransitionScrollProgress - 50) / 24, 1));
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

  function heatmapMetricValue(cell: HeatmapCell, outcome: ShotOutcome) {
    if (outcome === 'made') return cell.made;
    if (outcome === 'missed') return cell.missed;
    return cell.attempts;
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
      <section class="order-4 mt-10" use:observeScene={1}>
        <article class="panel overflow-hidden border border-amber-300/20 bg-slate-900/90">
          <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1.35fr)] lg:px-8">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300/80">Scene 1</p>
              <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Volume and efficiency by distance.</h2>
              <p class="mt-4 text-sm leading-7 text-slate-300">
                This chart makes the original tradeoff visible. Shots near the rim are converted at the highest rates,
                but volume does not stay there. As distance increases, accuracy drops, yet teams still keep a large diet
                of longer attempts because the value structure of the court changes at the three-point line.
              </p>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Current Lens</p>
                <p class="mt-2 text-2xl font-bold text-white">{shotOutcomeLabel}</p>
                <p class="mt-1 text-sm text-slate-400">{headlineSeason}</p>
              </div>

              <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">How To Read It</p>
                <p class="mt-2 text-sm leading-6 text-slate-300">
                  The x-axis shows shot distance and each stacked bar splits attempts into made and missed shots.
                  Use the chart toggle to animate between raw attempts and percentage share, so you can compare
                  both volume and efficiency patterns without switching to a second axis.
                </p>
              </div>
            </div>
          </div>

          <div class="border-b border-white/10 px-6 py-5 lg:px-8">
            <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div class="min-w-0 flex-1">
                <FilterBar seasons={data.seasons} filter={displayedFilter} on:change={(event) => handleFilterChange(event.detail)} />
              </div>

              <button
                type="button"
                class:active-highlight={distanceHighlightActive}
                class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm font-semibold text-slate-300 transition hover:border-amber-300/40 hover:text-white"
                on:click={() => (distanceHighlightActive = !distanceHighlightActive)}
              >
                {distanceHighlightActive ? 'Hide 3PT Highlight' : 'Highlight 3PT Range'}
              </button>
            </div>
            <p class="mt-4 text-xs leading-6 text-slate-400">
              This shared filter drives the distance profile and the later court views. The distance chart honors the selected
              shot lens, while the heatmap transition keeps its own fixed all-shot and made-shot views.
            </p>
          </div>

          <div class="min-h-[26rem] px-6 py-6 lg:min-h-[34rem] lg:px-8">
            <DistanceChart
              data={selectedDistance}
              shotOutcome={filter.shotOutcome}
              longDistanceBucket={data.distance?.metadata.longDistanceBucket ?? 40}
              highlightThreePointRange={distanceHighlightActive}
            />
          </div>
        </article>
      </section>

      <section class="order-6 mt-10" use:observeScene={2}>
        <Scroll bind:progress={heatmapTransitionScrollProgress} threshold={0.48} margin={8}>
          {#snippet children()}
            <div>
              <article class="panel min-h-[140vh] border border-teal-300/20 bg-slate-900/90 p-6 sm:p-8">
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/80">Scene 2</p>
                <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Shot volume and made-shot hotspots</h2>
                <p class="mt-4 text-sm leading-7 text-slate-300">
                  As you scroll, the court should first look crowded at the rim and around the three-point line. Then, as
                  the view shifts to made shots, those same areas stay bright while the midrange remains relatively quiet.
                </p>

                <div class="mt-8 grid gap-4 sm:grid-cols-2">
                  <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Transition Start</p>
                    <p class="mt-2 text-2xl font-bold text-white">All shots</p>
                    <p class="mt-1 text-sm text-slate-400">{heatmapSeasonLabel}</p>
                    <p class="mt-2 text-sm leading-6 text-slate-300">
                      At the start, notice where attempts pile up. The rim is the strongest hotspot, and the three-point
                      arc forms a clear band of volume around it.
                    </p>
                  </div>

                  <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
                    <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Transition End</p>
                    <p class="mt-2 text-2xl font-bold text-white">Made shots</p>
                    <p class="mt-1 text-sm text-slate-400">{heatmapSeasonLabel}</p>
                    <p class="mt-2 text-sm leading-6 text-slate-300">
                      By the end, look for the areas that stay bright when the map switches to makes. The paint still
                      stands out most, and the best perimeter zones become easier to pick out.
                    </p>
                  </div>
                </div>

                <p class="mt-8 text-sm leading-7 text-slate-300">
                  Teams take most of
                  their shots either at the rim or from three, and the rim remains the clearest center of both volume and
                  makes. You should also notice that above-the-break threes appear more often than corner threes, while
                  the midrange stays comparatively sparse, showing how little modern offenses want to live in that space.
                </p>
              </article>
            </div>
          {/snippet}

          {#snippet viz()}
            <article class="panel overflow-hidden border border-emerald-300/20 bg-slate-900/90">
              <div class="border-b border-white/10 px-6 py-5 lg:px-8">
                <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <p class="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300/80">Scene 2</p>
                    <h3 class="mt-2 text-2xl font-bold text-white">Court heatmap transition</h3>
                    <p class="mt-2 text-sm leading-6 text-slate-400">
                      {#if heatmapFadeProgress < 0.5}
                        Volume heatmap
                      {:else}
                        Made-shot density heatmap
                      {/if}
                    </p>
                  </div>

                  <label class="flex items-center gap-3 text-sm text-slate-300">
                    <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Season</span>
                    <select
                      class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-emerald-400/60"
                      bind:value={heatmapSeason}
                    >
                      <option value="all">All seasons</option>
                      {#each data.seasons as season}
                        <option value={season}>{season}</option>
                      {/each}
                    </select>
                  </label>
                </div>
              </div>
              <div class="min-h-[30rem] px-6 py-6 lg:min-h-[40rem] lg:px-8">
                <div class="grid h-full min-h-[26rem] w-full">
                  <div
                    class="col-start-1 row-start-1 h-full transition-opacity duration-500"
                    style={`opacity: ${1 - heatmapFadeProgress}; pointer-events: ${heatmapFadeProgress < 0.98 ? 'auto' : 'none'}; z-index: ${heatmapFadeProgress < 0.98 ? 20 : 10};`}
                  >
                    <CourtHeatmap
                      cells={selectedHeatmap}
                      shotOutcome="all"
                      cellSize={data.heatmap?.metadata.cellSize ?? 2}
                      halfCourtLength={data.heatmap?.metadata.halfCourtLength ?? 47}
                      halfCourtWidth={data.heatmap?.metadata.halfCourtWidth ?? 25}
                    />
                  </div>

                  <div
                    class="col-start-1 row-start-1 h-full transition-opacity duration-500"
                    style={`opacity: ${heatmapFadeProgress}; pointer-events: ${heatmapFadeProgress >= 0.98 ? 'auto' : 'none'}; z-index: ${heatmapFadeProgress >= 0.98 ? 20 : 10};`}
                  >
                    <CourtHeatmap
                      cells={selectedHeatmap}
                      shotOutcome="made"
                      cellSize={data.heatmap?.metadata.cellSize ?? 2}
                      halfCourtLength={data.heatmap?.metadata.halfCourtLength ?? 47}
                      halfCourtWidth={data.heatmap?.metadata.halfCourtWidth ?? 25}
                    />
                  </div>
                </div>
              </div>
            </article>
          {/snippet}
        </Scroll>
      </section>

      <section class="order-7 mt-10" use:observeScene={3}>
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
                  {#each data.seasons as season}
                    <option value={season}>{season}</option>
                  {/each}
                </select>
              </label>
            </div>
          </div>

          <div class="min-h-[30rem] px-3 py-3 sm:px-4 sm:py-4 lg:min-h-[40rem] lg:px-5 lg:py-5">
            <CourtHeatmap3D
              cells={selectedHeatmap}
              shotOutcome={heatmap3dOutcome}
              cellSize={data.heatmap?.metadata.cellSize ?? 2}
              halfCourtLength={data.heatmap?.metadata.halfCourtLength ?? 47}
              halfCourtWidth={data.heatmap?.metadata.halfCourtWidth ?? 25}
            />
          </div>
        </article>
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
                </p>
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

      <section class="order-8 relative left-1/2 mt-10 w-screen -translate-x-1/2 px-6 sm:px-8 lg:px-10 xl:px-12">
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
                  </p>
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

      <section class="order-9 mt-10">
        <article class="panel overflow-hidden border border-indigo-300/25 bg-slate-900/90">
          <div class="grid gap-8 border-b border-white/10 px-6 py-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,1.85fr)] lg:px-8">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-indigo-200/80">3D Shot Timeline</p>
              <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">See the evolution play out across the floor.</h2>
              <p class="mt-4 text-sm leading-7 text-slate-300">
                Watch the spatial shift unfold in this animated 3D shot map. Each shot animates in its original court location, so you can see how the distribution of attempts and makes changes over time in different zones of the floor.
              </p>
            </div>

            <div class="grid gap-4 sm:grid-cols-2">
              <div class="rounded-3xl border border-white/10 bg-slate-950/70 px-5 py-5">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Timeline Scope</p>
                <p class="mt-3 text-2xl font-bold text-white">{shot3dSeason === 'all' ? 'All Seasons' : shot3dSeason}</p>
                <p class="mt-2 text-sm leading-6 text-slate-400">
                  {shot3dProfileMode === 'player'
                    ? 'Player mode weights shot distribution by the selected player profile for easier season-to-season comparison.'
                    : 'League mode shows the full league distribution for the selected season scope.'}
                </p>
              </div>

              <div class="rounded-3xl border border-white/10 bg-slate-950/70 px-5 py-5">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">How to read</p>
                <p class="mt-2 text-sm leading-6 text-slate-400">
                  Teal arcs are made shots and orange arcs are misses. Use the season selector to jump directly, then use
                  play and repeat to compare eras.
                </p>
              </div>
            </div>
          </div>

          <div class="border-b border-white/10 px-6 py-5 lg:px-8">
            <div class="flex flex-wrap items-end gap-4">
              <div class="inline-flex shrink-0 rounded-2xl border border-white/10 bg-slate-950/90 p-1">
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

              <div class="inline-flex shrink-0 rounded-2xl border border-white/10 bg-slate-950/90 p-1">
                {#each [
                  { value: 'league', label: 'League' },
                  { value: 'player', label: 'Player weighted' }
                ] as option}
                  <button
                    type="button"
                    class:selected={shot3dProfileMode === option.value}
                    class="rounded-xl px-4 py-2 text-sm font-semibold text-slate-300 transition hover:text-white"
                    on:click={() => (shot3dProfileMode = option.value as 'league' | 'player')}
                  >
                    {option.label}
                  </button>
                {/each}
              </div>

              <label class="flex min-w-0 items-center gap-3 text-sm text-slate-300">
                <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Season</span>
                <select
                  class="w-44 max-w-[65vw] rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-indigo-400/60"
                  bind:value={shot3dSeason}
                  on:change={handleShot3dSeasonChange}
                >
                  <option value="all">All seasons</option>
                  {#each shot3dProfileMode === 'player' ? shot3dPlayerSeasonOptions : data.seasons as season}
                    <option value={season}>{season}</option>
                  {/each}
                </select>
              </label>

              {#if shot3dProfileMode === 'player'}
                <label class="flex min-w-0 items-center gap-3 text-sm text-slate-300">
                  <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Player</span>
                  <select
                    class="w-52 max-w-[68vw] rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-indigo-400/60"
                    bind:value={shot3dPlayer}
                    on:change={handleShot3dPlayerChange}
                  >
                    {#each shot3dPlayerCandidates as player}
                      <option value={player.player}>{player.player}</option>
                    {/each}
                  </select>
                </label>
              {/if}

              <label class="flex shrink-0 items-center gap-3 text-sm text-slate-300">
                <span class="font-semibold uppercase tracking-[0.18em] text-slate-400">Speed</span>
                <input
                  type="range"
                  min="0.5"
                  max="2.5"
                  step="0.1"
                  bind:value={shot3dSpeed}
                  class="h-2 w-32 accent-indigo-300"
                />
                <span class="w-10 text-right text-slate-300">{shot3dSpeed.toFixed(1)}x</span>
              </label>

              <div class="flex shrink-0 items-center gap-2 lg:ml-auto">
                <button
                  type="button"
                  class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-white/20 hover:text-white"
                  on:click={() => (shot3dPlaying = !shot3dPlaying)}
                >
                  {shot3dPlaying ? 'Pause' : 'Play'}
                </button>
                <button
                  type="button"
                  class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-white/20 hover:text-white"
                  on:click={() => (shot3dLoop = !shot3dLoop)}
                >
                  {shot3dLoop ? 'Repeat on' : 'Repeat off'}
                </button>
              </div>
            </div>
          </div>

          <div class="p-3 sm:p-4 lg:p-5">
            <ShotTimeline3D
              heatmap={data.heatmap}
              seasons={data.seasons}
              selectedSeason={shot3dSeason}
              shotOutcome={shot3dOutcome}
              profileMode={shot3dProfileMode}
              playerTargetDistance={shot3dProfileMode === 'player' ? selectedPlayerDistanceTarget : null}
              speed={shot3dSpeed}
              playing={shot3dPlaying}
              loopSeasons={shot3dLoop}
              showControls={true}
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
