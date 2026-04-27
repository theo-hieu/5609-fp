<script lang="ts">
  import Scroll from '$lib/components/Scroll.svelte';
  import type { SeasonDistanceTrend, ShotTypeSeasonTrend, ZoneSeasonTrend } from '$lib/types';

  export let seasonDistance: SeasonDistanceTrend[] = [];
  export let shotTypeTrend: ShotTypeSeasonTrend[] = [];
  export let zoneTrend: ZoneSeasonTrend[] = [];
  export let zones: string[] = [];

  type LegendItem = { key: string; label: string; color: string };
  type Point = { x: number; y: number; value: number; season: string };
  type Series = { key: string; label: string; color: string; values: number[]; points: Point[] };

  const width = 920;
  const height = 640;
  const left = 72;
  const right = 36;
  const plotWidth = width - left - right;
  const panels = [
    { key: 'distance', title: 'Average distance', y: 56, height: 136, unit: 'ft' },
    { key: 'mix', title: 'Shot type share', y: 250, height: 136, unit: '%' },
    { key: 'zone', title: 'Zone share', y: 444, height: 136, unit: '%' }
  ];

  const zoneColors: Record<string, string> = {
    'Restricted Area': '#fde68a',
    'In The Paint (Non-RA)': '#fbbf24',
    'Mid-Range': '#fb923c',
    'Left Corner 3': '#38bdf8',
    'Right Corner 3': '#0ea5e9',
    'Above the Break 3': '#14b8a6',
    Backcourt: '#64748b'
  };

  let progress = 0;
  let hoverIndex: number | null = null;
  let hoverX: number | null = null;
  let svgElement: SVGSVGElement | null = null;
  let filterStartIndex = 0;
  let filterEndIndex: number | null = null;
  let dragStartX: number | null = null;
  let dragCurrentX: number | null = null;
  let isDragging = false;

  const clamp = (value: number, min = 0, max = 1) => Math.min(Math.max(value, min), max);
  const percent = (value: number) => `${value.toFixed(1)}%`;

  function stageReveal(start: number, end: number) {
    return clamp((progress - start) / Math.max(end - start, 1));
  }

  function rowByShotType(row: ShotTypeSeasonTrend, shotType: string) {
    return row.shotTypes.find((entry) => entry.shotType === shotType);
  }

  function rowByZone(row: ZoneSeasonTrend, zone: string) {
    return row.zones.find((entry) => entry.zone === zone);
  }

  function scaleX(index: number, total: number) {
    if (total <= 1) return left;
    return left + (index / (total - 1)) * plotWidth;
  }

  function scaleY(value: number, min: number, max: number, panelY: number, panelHeight: number) {
    const range = Math.max(max - min, 0.0001);
    return panelY + panelHeight - ((value - min) / range) * panelHeight;
  }

  function clampIndex(index: number, total: number) {
    return Math.max(0, Math.min(Math.round(index), Math.max(total - 1, 0)));
  }

  function makePoints(values: number[], seasons: string[], min: number, max: number, panelY: number, panelHeight: number) {
    return values.map((value, index) => ({
      x: scaleX(index, values.length),
      y: scaleY(value, min, max, panelY, panelHeight),
      value,
      season: seasons[index] ?? ''
    }));
  }

  function pathFromPoints(points: Point[]) {
    if (!points.length) return '';
    return points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(' ');
  }

  function shareChange(series: Series | null) {
    if (!series || !series.values.length) return 'N/A';
    const first = series.values[0] ?? 0;
    const last = series.values[series.values.length - 1] ?? 0;
    return `${first.toFixed(1)}% to ${last.toFixed(1)}%`;
  }

  function makeTicks(min: number, max: number, count = 3) {
    if (count <= 1) return [min];
    const range = Math.max(max - min, 0.0001);
    return Array.from({ length: count }, (_, index) => min + (range * index) / (count - 1));
  }

  function tickLabel(value: number, unit: string) {
    if (unit === 'ft') return value.toFixed(1);
    return `${Math.round(value)}%`;
  }

  function seasonTickIndexes(total: number) {
    if (total <= 0) return [];
    if (total === 1) return [0];
    const step = total > 28 ? 3 : total > 14 ? 2 : 1;
    const indexes = Array.from({ length: Math.ceil(total / step) }, (_, index) => index * step).filter((index) => index < total);
    return indexes.includes(total - 1) ? indexes : [...indexes, total - 1];
  }

  function legendStart(items: LegendItem[]) {
    return Math.max(left + 178, left + plotWidth - items.length * 118);
  }

  function pointAt(series: Series | null, index: number) {
    return series?.points[Math.max(0, Math.min(index, series.points.length - 1))] ?? null;
  }

  function seriesValue(series: Series | null, index: number, unit: string) {
    const value = series?.values[Math.max(0, Math.min(index, (series?.values.length ?? 1) - 1))];
    if (value == null) return 'N/A';
    if (unit === 'ft') return `${value.toFixed(2)} ft`;
    return percent(value);
  }

  function seasonDateLabel(season: string) {
    return season === 'N/A' ? 'Season unavailable' : `Season: ${season}`;
  }

  function eventToViewX(event: PointerEvent) {
    if (!svgElement) return left;
    const rect = svgElement.getBoundingClientRect();
    const viewX = ((event.clientX - rect.left) / Math.max(rect.width, 1)) * width;
    return Math.min(Math.max(viewX, left), left + plotWidth);
  }

  function indexFromViewX(viewX: number, total: number) {
    const rawIndex = ((viewX - left) / plotWidth) * Math.max(total - 1, 0);
    return clampIndex(rawIndex, total);
  }

  function handlePointerDown(event: PointerEvent) {
    if (!visibleSeasons.length) return;
    event.preventDefault();
    const viewX = eventToViewX(event);
    dragStartX = viewX;
    dragCurrentX = viewX;
    hoverX = viewX;
    isDragging = true;
    hoverIndex = indexFromViewX(viewX, visibleSeasons.length);
    (event.currentTarget as HTMLElement).setPointerCapture?.(event.pointerId);
  }

  function handlePointerMove(event: PointerEvent) {
    if (!visibleSeasons.length) return;
    if (visibleSeasons.length === 1) {
      hoverIndex = 0;
      return;
    }
    const viewX = eventToViewX(event);
    hoverX = viewX;
    if (isDragging) dragCurrentX = viewX;
    hoverIndex = indexFromViewX(viewX, visibleSeasons.length);
  }

  function handlePointerUp(event: PointerEvent) {
    if (!isDragging) return;
    const endX = eventToViewX(event);
    dragCurrentX = endX;
    (event.currentTarget as HTMLElement).releasePointerCapture?.(event.pointerId);

    if (dragStartX != null && Math.abs(endX - dragStartX) > 8 && visibleSeasons.length > 1) {
      const startIndex = indexFromViewX(Math.min(dragStartX, endX), visibleSeasons.length);
      const endIndex = indexFromViewX(Math.max(dragStartX, endX), visibleSeasons.length);
      if (endIndex > startIndex) {
        filterStartIndex = normalizedStartIndex + startIndex;
        filterEndIndex = normalizedStartIndex + endIndex;
        hoverIndex = 0;
        hoverX = left;
      }
    }

    isDragging = false;
    dragStartX = null;
    dragCurrentX = null;
  }

  function clearHover() {
    if (isDragging) return;
    hoverIndex = null;
    hoverX = null;
  }

  function resetRange() {
    filterStartIndex = 0;
    filterEndIndex = null;
    hoverIndex = null;
    hoverX = null;
    isDragging = false;
    dragStartX = null;
    dragCurrentX = null;
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    const delta = event.key === 'ArrowLeft' ? -1 : 1;
    hoverIndex = clampIndex((hoverIndex ?? activeIndex) + delta, visibleSeasons.length);
  }

  $: seasons = seasonDistance.map((row) => row.season);
  $: fullEndIndex = Math.max(seasons.length - 1, 0);
  $: normalizedStartIndex = Math.min(Math.max(filterStartIndex, 0), fullEndIndex);
  $: normalizedEndIndex = Math.max(
    normalizedStartIndex,
    Math.min(filterEndIndex ?? fullEndIndex, fullEndIndex)
  );
  $: visibleSeasons = seasons.slice(normalizedStartIndex, normalizedEndIndex + 1);
  $: visibleSeasonDistance = seasonDistance.slice(normalizedStartIndex, normalizedEndIndex + 1);
  $: visibleShotTypeTrend = shotTypeTrend.slice(normalizedStartIndex, normalizedEndIndex + 1);
  $: visibleZoneTrend = zoneTrend.slice(normalizedStartIndex, normalizedEndIndex + 1);
  $: isRangeFiltered = normalizedStartIndex > 0 || normalizedEndIndex < fullEndIndex;
  $: hasCoreData = seasonDistance.length > 0;
  $: hasMixData = shotTypeTrend.length > 0;
  $: hasZoneData = zoneTrend.length > 0;
  $: hasCoordinatedData = hasCoreData && hasMixData && hasZoneData;
  $: missingDataLabels = [
    !hasCoreData ? 'season distance' : '',
    !hasMixData ? 'shot type share' : '',
    !hasZoneData ? 'court zone share' : ''
  ].filter(Boolean);
  $: if (hoverIndex != null && hoverIndex >= visibleSeasons.length) hoverIndex = null;
  $: scrollIndex = visibleSeasons.length > 1 ? Math.round(clamp(progress / 100) * (visibleSeasons.length - 1)) : 0;
  $: activeIndex = hoverIndex ?? scrollIndex;
  $: activeSeason = visibleSeasons[Math.max(0, Math.min(activeIndex, visibleSeasons.length - 1))] ?? 'N/A';
  $: activeSeasonDate = seasonDateLabel(activeSeason);
  $: stage = progress < 34 ? 1 : progress < 68 ? 2 : 3;
  $: isHovering = hoverIndex != null;

  $: distanceValues = visibleSeasonDistance.map((row) => row.avgShotDistance);
  $: distanceMin = distanceValues.length ? Math.max(0, Math.min(...distanceValues) - 0.65) : 0;
  $: distanceMax = distanceValues.length ? Math.max(...distanceValues) + 0.65 : 1;
  $: distanceTicks = makeTicks(distanceMin, distanceMax, 3);
  $: distancePoints = makePoints(distanceValues, visibleSeasons, distanceMin, distanceMax, panels[0].y, panels[0].height);
  $: distanceSeries = {
    key: 'distance',
    label: 'Avg shot distance',
    color: '#fbbf24',
    values: distanceValues,
    points: distancePoints
  } satisfies Series;

  $: mixSeasons = visibleShotTypeTrend.map((row) => row.season);
  $: twoPointValues = visibleShotTypeTrend.map((row) => +(100 * (rowByShotType(row, '2PT Field Goal')?.share ?? 0)).toFixed(1));
  $: threePointValues = visibleShotTypeTrend.map((row) => +(100 * (rowByShotType(row, '3PT Field Goal')?.share ?? 0)).toFixed(1));
  $: mixTicks = [0, 50, 100];
  $: twoPointSeries = {
    key: 'two',
    label: '2PT share',
    color: '#fb923c',
    values: twoPointValues,
    points: makePoints(twoPointValues, mixSeasons, 0, 100, panels[1].y, panels[1].height)
  } satisfies Series;
  $: threePointSeries = {
    key: 'three',
    label: '3PT share',
    color: '#14b8a6',
    values: threePointValues,
    points: makePoints(threePointValues, mixSeasons, 0, 100, panels[1].y, panels[1].height)
  } satisfies Series;

  $: zoneSeasons = visibleZoneTrend.map((row) => row.season);
  $: featuredZones = ['Mid-Range', 'Left Corner 3', 'Right Corner 3', 'Above the Break 3'].filter(
    (zone) => zones.includes(zone) || zoneTrend.some((row) => row.zones.some((entry) => entry.zone === zone))
  );
  $: zoneValuesByName = featuredZones.map((zone) =>
    visibleZoneTrend.map((row) => +(100 * (rowByZone(row, zone)?.share ?? 0)).toFixed(1))
  );
  $: zoneMax = Math.max(8, Math.ceil((Math.max(0, ...zoneValuesByName.flat()) + 2) / 2) * 2);
  $: zoneTicks = [0, zoneMax / 2, zoneMax];
  $: zoneSeries = featuredZones.map((zone, index) => ({
    key: zone,
    label: zone,
    color: zoneColors[zone] ?? '#cbd5e1',
    values: zoneValuesByName[index] ?? [],
    points: makePoints(zoneValuesByName[index] ?? [], zoneSeasons, 0, zoneMax, panels[2].y, panels[2].height)
  })) satisfies Series[];

  $: aboveBreakSeries = zoneSeries.find((series) => series.key === 'Above the Break 3') ?? null;
  $: leftCornerSeries = zoneSeries.find((series) => series.key === 'Left Corner 3') ?? null;
  $: rightCornerSeries = zoneSeries.find((series) => series.key === 'Right Corner 3') ?? null;
  $: midRangeSeries = zoneSeries.find((series) => series.key === 'Mid-Range') ?? null;

  $: distanceReveal = stageReveal(0, 30);
  $: mixReveal = stageReveal(24, 62);
  $: zoneReveal = stageReveal(58, 94);
  $: distanceClipWidth = plotWidth * distanceReveal;
  $: mixClipWidth = plotWidth * mixReveal;
  $: zoneClipWidth = plotWidth * zoneReveal;
  $: activeX = scaleX(activeIndex, visibleSeasons.length);
  $: activeGuideX = isHovering ? (hoverX ?? activeX) : activeX;
  $: distanceActivePoint = distanceSeries.points[Math.max(0, Math.min(activeIndex, distanceSeries.points.length - 1))];
  $: mixActivePoints = [twoPointSeries, threePointSeries].map((series) => pointAt(series, activeIndex));
  $: zoneActivePoints = zoneSeries.map((series) => pointAt(series, activeIndex));
  $: xTickIndexes = seasonTickIndexes(visibleSeasons.length);
  $: brushX = isDragging && dragStartX != null && dragCurrentX != null ? Math.min(dragStartX, dragCurrentX) : 0;
  $: brushWidth = isDragging && dragStartX != null && dragCurrentX != null ? Math.abs(dragCurrentX - dragStartX) : 0;
  $: distanceLegend = [{ key: distanceSeries.key, label: distanceSeries.label, color: distanceSeries.color }];
  $: mixLegend = [twoPointSeries, threePointSeries].map(({ key, label, color }) => ({ key, label, color }));
  $: zoneLegend = zoneSeries.map(({ key, label, color }) => ({ key, label, color }));
  $: tooltipWidth = 224;
  $: tooltipX = Math.min(activeGuideX + 14, left + plotWidth - tooltipWidth - 6);
  $: tooltipY = panels[0].y + 10;
  $: tooltipRows = [
    { label: 'Avg distance', value: seriesValue(distanceSeries, activeIndex, 'ft'), color: distanceSeries.color },
    { label: '3PT share', value: seriesValue(threePointSeries, activeIndex, '%'), color: threePointSeries.color },
    { label: '2PT share', value: seriesValue(twoPointSeries, activeIndex, '%'), color: twoPointSeries.color },
    { label: 'Above break', value: seriesValue(aboveBreakSeries, activeIndex, '%'), color: aboveBreakSeries?.color ?? '#14b8a6' },
    { label: 'Mid-range', value: seriesValue(midRangeSeries, activeIndex, '%'), color: midRangeSeries?.color ?? '#fb923c' }
  ];

  $: firstSeason = visibleSeasons[0] ?? 'first season';
  $: lastSeason = visibleSeasons[visibleSeasons.length - 1] ?? 'latest season';
  $: distanceChange = distanceValues.length
    ? `${distanceValues[0].toFixed(2)} ft to ${distanceValues[distanceValues.length - 1].toFixed(2)} ft`
    : 'N/A';
</script>

<section class="relative left-1/2 order-1 mt-10 w-screen -translate-x-1/2 px-4 sm:px-6 lg:px-8">
  <div class="mx-auto max-w-[118rem]">
  <Scroll
    bind:progress
    threshold={0.62}
    margin={8}
    storyWidth="minmax(20rem, 0.74fr)"
    vizWidth="minmax(0, 1.9fr)"
    gap="1.5rem"
  >
    {#snippet children()}
      <div class="space-y-6">
        <article class:active={stage === 1} class="story-card panel border border-amber-300/20 bg-slate-900/90 p-5 sm:p-6">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300/80">Mechanism 1</p>
          <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">The league drifts farther from the rim.</h2>
          <p class="mt-4 text-sm leading-7 text-slate-300">
            Start with the headline: average shot distance rises from {firstSeason} to {lastSeason}. The animation
            reveals this as a timeline, but the point is not just that the line goes up; it sets up a question about
            what moved underneath it.
          </p>
          <p class="mt-3 text-sm leading-7 text-slate-400">
            Think of shot distance as the league&apos;s center of gravity: when more attempts move behind the 3-point
            line, the average shot gets farther away even if every individual player does not suddenly become a deep
            shooter.
          </p>
          <div class="mt-5 rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Distance Change</p>
            <p class="mt-2 text-2xl font-bold text-white">{distanceChange}</p>
            <p class="mt-1 text-sm text-slate-400">Active season: {activeSeason}</p>
          </div>
        </article>

        <article class:active={stage === 2} class="story-card panel min-h-[72vh] border border-cyan-300/20 bg-slate-900/90 p-5 sm:p-6">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300/80">Mechanism 2</p>
          <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">The extra distance comes from shot mix.</h2>
          <p class="mt-4 text-sm leading-7 text-slate-300">
            The middle layer answers the first question: three-point share climbs while two-point share falls. That
            makes the average-distance increase less mysterious. The league is reallocating attempts across the arc,
            not merely stretching long twos a little farther out.
          </p>
          <p class="mt-3 text-sm leading-7 text-slate-400">
            Shot share means the percentage of all attempts that belong to a category. A rising 3PT share means more
            possessions are ending behind the arc instead of inside it.
          </p>
          <div class="mt-5 grid gap-4 sm:grid-cols-2">
            <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">3PT Share</p>
              <p class="mt-2 text-2xl font-bold text-teal-200">{shareChange(threePointSeries)}</p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4">
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">2PT Share</p>
              <p class="mt-2 text-2xl font-bold text-orange-200">{shareChange(twoPointSeries)}</p>
            </div>
          </div>
        </article>

        <article class:active={stage === 3} class="story-card panel min-h-[78vh] border border-rose-300/20 bg-slate-900/90 p-5 sm:p-6">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-rose-300/80">Mechanism 3</p>
          <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">Above-the-break threes carry the spatial shift.</h2>
          <p class="mt-4 text-sm leading-7 text-slate-300">
            The bottom layer breaks the arc apart. Corner threes matter, but they stay comparatively stable. The big
            movement is above the break, paired with the collapse of mid-range share. This is the modern shot profile:
            rim pressure, spacing, and fewer in-between attempts.
          </p>
          <p class="mt-3 text-sm leading-7 text-slate-400">
            Above the break is the curved part of the 3-point line near the top and wings. Corner threes come from the
            short straight sections near the baseline, while mid-range shots live between the paint and the arc.
          </p>
          <div class="mt-5 grid gap-3 text-sm text-slate-300 sm:grid-cols-2">
            <p class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
              <span class="font-semibold text-teal-200">Above break:</span> {shareChange(aboveBreakSeries)}
            </p>
            <p class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
              <span class="font-semibold text-orange-200">Mid-range:</span> {shareChange(midRangeSeries)}
            </p>
            <p class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
              <span class="font-semibold text-sky-200">Left corner:</span> {shareChange(leftCornerSeries)}
            </p>
            <p class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
              <span class="font-semibold text-blue-200">Right corner:</span> {shareChange(rightCornerSeries)}
            </p>
          </div>
        </article>
      </div>
    {/snippet}

    {#snippet viz()}
      <article class="panel coordinated-viz overflow-hidden border border-amber-300/20 bg-slate-900/90">
        <div class="border-b border-white/10 px-5 py-5 sm:px-6 lg:px-8">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300/80">Coordinated View</p>
              <h3 class="mt-2 text-2xl font-bold text-white">How shot distance, shot type, and court zones move together</h3>
              <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                Scroll anywhere on the page to reveal the causal chain instead of reading three disconnected charts.
              </p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-slate-300">
              <p class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Stage</p>
              <p class="mt-1 font-bold text-white">
                {stage === 1 ? 'Distance rises' : stage === 2 ? '3PT share absorbs attempts' : 'Above-break threes explain where'}
              </p>
              {#if isRangeFiltered}
                <div class="mt-3 flex items-center justify-between gap-3 border-t border-white/10 pt-3">
                  <p class="text-xs font-semibold text-slate-400">{firstSeason} to {lastSeason}</p>
                  <button
                    type="button"
                    class="rounded-md border border-white/10 px-2 py-1 text-xs font-bold text-slate-200 transition hover:border-white/25 hover:text-white"
                    on:click={resetRange}
                  >
                    Reset
                  </button>
                </div>
              {/if}
            </div>
          </div>
        </div>

        <div class="p-3 sm:p-5 lg:p-6">
          {#if hasCoordinatedData}
            <div
              class="mechanism-board rounded-3xl border border-white/10 bg-slate-950/70 p-2 sm:p-4"
              role="slider"
              tabindex="0"
              aria-label="Inspect seasons in the coordinated shot evolution chart"
              aria-valuemin="0"
              aria-valuemax={Math.max(visibleSeasons.length - 1, 0)}
              aria-valuenow={activeIndex}
              aria-valuetext={activeSeason}
              on:pointermove={handlePointerMove}
              on:pointerleave={clearHover}
              on:pointerdown={handlePointerDown}
              on:pointerup={handlePointerUp}
              on:pointercancel={handlePointerUp}
              on:keydown={handleKeydown}
            >
              <svg
                bind:this={svgElement}
                viewBox={`0 0 ${width} ${height}`}
                role="img"
                aria-label="Coordinated shot evolution mechanism chart"
              >
                <defs>
                  <clipPath id="distance-clip"><rect x={left} y="0" width={distanceClipWidth} height={height} /></clipPath>
                  <clipPath id="mix-clip"><rect x={left} y="0" width={mixClipWidth} height={height} /></clipPath>
                  <clipPath id="zone-clip"><rect x={left} y="0" width={zoneClipWidth} height={height} /></clipPath>
                </defs>

                {#each panels as panel, panelIndex}
                  <g>
                    <rect x={left} y={panel.y} width={plotWidth} height={panel.height} rx="18" fill="rgba(15, 23, 42, 0.76)" stroke="rgba(148, 163, 184, 0.13)" />
                    <text x="24" y={panel.y + 22} fill="#cbd5e1" font-size="15" font-weight="700">{panel.title}</text>
                    <text x={left - 44} y={panel.y + 43} fill="#64748b" font-size="10" font-weight="700" text-anchor="middle">{panel.unit}</text>
                    <line x1={left} x2={left + plotWidth} y1={panel.y + panel.height} y2={panel.y + panel.height} stroke="rgba(148, 163, 184, 0.28)" />
                    <line x1={left} x2={left} y1={panel.y} y2={panel.y + panel.height} stroke="rgba(148, 163, 184, 0.24)" />

                    {#each panelIndex === 0 ? distanceTicks : panelIndex === 1 ? mixTicks : zoneTicks as tick}
                      <g>
                        <line
                          x1={left}
                          x2={left + plotWidth}
                          y1={scaleY(tick, panelIndex === 0 ? distanceMin : 0, panelIndex === 0 ? distanceMax : panelIndex === 1 ? 100 : zoneMax, panel.y, panel.height)}
                          y2={scaleY(tick, panelIndex === 0 ? distanceMin : 0, panelIndex === 0 ? distanceMax : panelIndex === 1 ? 100 : zoneMax, panel.y, panel.height)}
                          stroke="rgba(148, 163, 184, 0.1)"
                        />
                        <text
                          x={left - 10}
                          y={scaleY(tick, panelIndex === 0 ? distanceMin : 0, panelIndex === 0 ? distanceMax : panelIndex === 1 ? 100 : zoneMax, panel.y, panel.height) + 4}
                          fill="#94a3b8"
                          font-size="11"
                          text-anchor="end"
                        >
                          {tickLabel(tick, panel.unit)}
                        </text>
                      </g>
                    {/each}
                  </g>
                {/each}

                {#each xTickIndexes as index}
                  <g>
                    <line x1={scaleX(index, visibleSeasons.length)} x2={scaleX(index, visibleSeasons.length)} y1={panels[0].y} y2={panels[2].y + panels[2].height} stroke="rgba(148, 163, 184, 0.06)" />
                    <line x1={scaleX(index, visibleSeasons.length)} x2={scaleX(index, visibleSeasons.length)} y1={panels[2].y + panels[2].height} y2={panels[2].y + panels[2].height + 6} stroke="rgba(148, 163, 184, 0.45)" />
                    <text x={scaleX(index, visibleSeasons.length)} y={height - 27} fill="#94a3b8" font-size="10.5" text-anchor={index === 0 ? 'start' : index === visibleSeasons.length - 1 ? 'end' : 'middle'}>{visibleSeasons[index]}</text>
                  </g>
                {/each}

                <g transform={`translate(${legendStart(distanceLegend)} ${panels[0].y + 20})`}>
                  {#each distanceLegend as item, index}
                    <g transform={`translate(${index * 118} 0)`}>
                      <line x1="0" x2="18" y1="0" y2="0" stroke={item.color} stroke-width="4" stroke-linecap="round" />
                      <text x="25" y="4" fill="#cbd5e1" font-size="11" font-weight="700">{item.label}</text>
                    </g>
                  {/each}
                </g>

                <g transform={`translate(${legendStart(mixLegend)} ${panels[1].y + 20})`}>
                  {#each mixLegend as item, index}
                    <g transform={`translate(${index * 118} 0)`}>
                      <line x1="0" x2="18" y1="0" y2="0" stroke={item.color} stroke-width="4" stroke-linecap="round" />
                      <text x="25" y="4" fill="#cbd5e1" font-size="11" font-weight="700">{item.label}</text>
                    </g>
                  {/each}
                </g>

                <g transform={`translate(${legendStart(zoneLegend)} ${panels[2].y + 20})`}>
                  {#each zoneLegend as item, index}
                    <g transform={`translate(${index * 118} 0)`}>
                      <line x1="0" x2="18" y1="0" y2="0" stroke={item.color} stroke-width="3.5" stroke-linecap="round" />
                      <text x="25" y="4" fill="#cbd5e1" font-size="10" font-weight="700">{item.label}</text>
                    </g>
                  {/each}
                </g>

                <g opacity="0.22">
                  <path d={pathFromPoints(distanceSeries.points)} fill="none" stroke={distanceSeries.color} stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
                  {#each [twoPointSeries, threePointSeries] as series}
                    <path d={pathFromPoints(series.points)} fill="none" stroke={series.color} stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
                  {/each}
                  {#each zoneSeries as series}
                    <path
                      d={pathFromPoints(series.points)}
                      fill="none"
                      stroke={series.color}
                      stroke-width={series.key === 'Above the Break 3' || series.key === 'Mid-Range' ? 3.4 : 2.2}
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      opacity={series.key === 'Above the Break 3' || series.key === 'Mid-Range' ? 1 : 0.62}
                    />
                  {/each}
                </g>

                <g opacity={stage >= 1 ? 1 : 0.55} clip-path="url(#distance-clip)">
                  <path d={pathFromPoints(distanceSeries.points)} fill="none" stroke={distanceSeries.color} stroke-width="5" stroke-linecap="round" stroke-linejoin="round" />
                  {#each distanceSeries.points as point, index}
                    {#if index === 0 || index === distanceSeries.points.length - 1 || index === activeIndex}
                      <circle cx={point.x} cy={point.y} r={index === activeIndex ? 6 : 4} fill="#fff7ed" stroke={distanceSeries.color} stroke-width="2.4" />
                    {/if}
                  {/each}
                </g>

                {#if distanceActivePoint}
                  <g opacity={distanceReveal > 0.16 ? 1 : 0}>
                    <line x1={activeGuideX} x2={activeGuideX} y1={panels[0].y - 16} y2={panels[2].y + panels[2].height + 14} stroke="rgba(248, 250, 252, 0.24)" stroke-dasharray="6 8" />
                    <text x={Math.min(activeGuideX + 12, left + plotWidth - 120)} y={panels[0].y - 4} fill="#f8fafc" font-size="13" font-weight="700">{activeSeason}</text>
                  </g>
                {/if}

                <g opacity={stage >= 2 ? 1 : 0.22} clip-path="url(#mix-clip)">
                  {#each [twoPointSeries, threePointSeries] as series}
                    <path d={pathFromPoints(series.points)} fill="none" stroke={series.color} stroke-width={series.key === 'three' ? 4.5 : 3.5} stroke-linecap="round" stroke-linejoin="round" />
                  {/each}
                </g>

                <g opacity={stage >= 3 ? 1 : 0.18} clip-path="url(#zone-clip)">
                  {#each zoneSeries as series}
                    <path
                      d={pathFromPoints(series.points)}
                      fill="none"
                      stroke={series.color}
                      stroke-width={series.key === 'Above the Break 3' || series.key === 'Mid-Range' ? 4.4 : 3}
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      opacity={series.key === 'Above the Break 3' || series.key === 'Mid-Range' ? 1 : 0.72}
                    />
                  {/each}
                </g>

                <g opacity={stage >= 2 ? 1 : 0} pointer-events="none">
                  <rect x={left + plotWidth * 0.42} y={panels[1].y - 30} width="270" height="22" rx="11" fill="rgba(15, 23, 42, 0.9)" stroke="rgba(20, 184, 166, 0.24)" />
                  <text x={left + plotWidth * 0.435} y={panels[1].y - 15} fill="#e2e8f0" font-size="11" font-weight="700">3PT share rises as average distance rises</text>
                </g>

                <g opacity={stage >= 3 ? 1 : 0} pointer-events="none">
                  <rect x={left + plotWidth * 0.38} y={panels[2].y - 30} width="292" height="22" rx="11" fill="rgba(15, 23, 42, 0.9)" stroke="rgba(20, 184, 166, 0.24)" />
                  <text x={left + plotWidth * 0.395} y={panels[2].y - 15} fill="#e2e8f0" font-size="11" font-weight="700">Above-the-break growth separates from corners</text>
                </g>

                {#if distanceActivePoint}
                  <g pointer-events="none">
                    <circle cx={distanceActivePoint.x} cy={distanceActivePoint.y} r={isHovering ? 7 : 5.5} fill="#fff7ed" stroke={distanceSeries.color} stroke-width="2.6" />
                    {#each mixActivePoints as point, index}
                      {#if point && (stage >= 2 || isHovering)}
                        <circle cx={point.x} cy={point.y} r={isHovering ? 5.5 : 4.5} fill="#0f172a" stroke={index === 0 ? twoPointSeries.color : threePointSeries.color} stroke-width="2.4" />
                      {/if}
                    {/each}
                    {#each zoneActivePoints as point, index}
                      {#if point && (stage >= 3 || isHovering)}
                        <circle cx={point.x} cy={point.y} r={isHovering ? 5 : 4} fill="#0f172a" stroke={zoneSeries[index].color} stroke-width="2.2" opacity={zoneSeries[index].key === 'Above the Break 3' || zoneSeries[index].key === 'Mid-Range' ? 1 : 0.78} />
                      {/if}
                    {/each}
                  </g>
                {/if}

                {#if isDragging && brushWidth > 2}
                  <g pointer-events="none">
                    <rect x={brushX} y={panels[0].y - 18} width={brushWidth} height={panels[2].y + panels[2].height + 30 - panels[0].y} fill="rgba(20, 184, 166, 0.16)" stroke="rgba(45, 212, 191, 0.58)" stroke-width="1.4" />
                    <line x1={brushX} x2={brushX} y1={panels[0].y - 18} y2={panels[2].y + panels[2].height + 12} stroke="rgba(240, 253, 250, 0.72)" />
                    <line x1={brushX + brushWidth} x2={brushX + brushWidth} y1={panels[0].y - 18} y2={panels[2].y + panels[2].height + 12} stroke="rgba(240, 253, 250, 0.72)" />
                  </g>
                {/if}

                {#if isHovering}
                  <g transform={`translate(${tooltipX} ${tooltipY})`} pointer-events="none">
                    <rect width={tooltipWidth} height="150" rx="12" fill="rgba(2, 6, 23, 0.94)" stroke="rgba(226, 232, 240, 0.2)" />
                    <text x="14" y="22" fill="#f8fafc" font-size="13" font-weight="800">{activeSeason}</text>
                    <text x={tooltipWidth - 14} y="22" fill="#94a3b8" font-size="10" font-weight="700" text-anchor="end">hover values</text>
                    {#each tooltipRows as row, index}
                      <g transform={`translate(14 ${43 + index * 17})`}>
                        <circle cx="0" cy="-3" r="3" fill={row.color} />
                        <text x="10" y="0" fill="#cbd5e1" font-size="11" font-weight="700">{row.label}</text>
                        <text x={tooltipWidth - 28} y="0" fill="#f8fafc" font-size="11" font-weight="800" text-anchor="end">{row.value}</text>
                      </g>
                    {/each}
                    <text x={tooltipWidth - 14} y="136" fill="#64748b" font-size="10.5" font-weight="700" text-anchor="end">{activeSeasonDate}</text>
                  </g>
                {/if}

                <rect x={left} y={panels[0].y - 18} width={plotWidth} height={panels[2].y + panels[2].height + 30 - panels[0].y} fill="transparent" />
              </svg>
            </div>
          {:else}
            <div class="flex min-h-[30rem] items-center justify-center rounded-3xl border border-dashed border-white/10 bg-slate-950/70 text-sm text-slate-400">
              Coordinated trend data is missing {missingDataLabels.join(', ')}. Re-run the data pipeline to generate season, shot type, and zone trends.
            </div>
          {/if}
        </div>
      </article>
    {/snippet}
  </Scroll>
  </div>
</section>

<style>
  .story-card {
    transition:
      border-color 240ms ease,
      opacity 240ms ease,
      transform 240ms ease;
  }

  .story-card:not(.active) {
    opacity: 0.72;
  }

  .story-card.active {
    border-color: rgba(251, 191, 36, 0.42);
    transform: translateY(-2px);
  }

  .mechanism-board svg {
    display: block;
    width: 100%;
    height: auto;
    min-height: min(42rem, calc(100vh - 14rem));
  }

  .mechanism-board {
    cursor: crosshair;
    touch-action: none;
  }

  .mechanism-board:focus-visible {
    outline: 2px solid rgba(20, 184, 166, 0.8);
    outline-offset: 4px;
  }

  .coordinated-viz {
    min-height: calc(100vh - 4rem);
  }

  @media (max-width: 640px) {
    .mechanism-board {
      overflow-x: auto;
    }

    .mechanism-board svg {
      min-width: 54rem;
      min-height: 30rem;
    }
  }
</style>

