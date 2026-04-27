<script lang="ts">
  import { onMount } from "svelte";
  import * as d3 from "d3";

  import type { HeatmapCell, ShotOutcome } from "$lib/types";

  export let cells: HeatmapCell[] = [];
  export let shotOutcome: ShotOutcome = "all";
  export let cellSize = 2;
  export let halfCourtLength = 47;
  export let halfCourtWidth = 25;

  type MetricConfig = {
    title: string;
    tooltipLabel: string;
    legendMinLabel: string;
    legendMaxLabel: string;
    legendNote: string;
    palette: string[];
    gradient: string;
    domain: [number, number];
    scale: "linear" | "log";
    getValue: (cell: HeatmapCell) => number;
    formatValue: (value: number) => string;
  };

  const volumePalette = ["#e2e8f0", "#7dd3fc", "#38bdf8", "#075985"];
  const efficiencyPalette = ["#ecfccb", "#86efac", "#22c55e", "#166534"];
  const missPalette = ["#fff7ed", "#fdba74", "#f97316", "#9a3412"];

  let container: HTMLDivElement;
  let chartRegion: HTMLDivElement;
  let svgElement: SVGSVGElement;
  let resizeObserver: ResizeObserver | null = null;
  let svgRenderWidth = 0;
  let svgRenderHeight = 0;

  let hoveredBin: HeatmapCell | null = null;
  let mousePos = { x: 0, y: 0 };

  function buildGradient(palette: string[]) {
    return `linear-gradient(90deg, ${palette.join(", ")})`;
  }

  function getMetricConfig(): MetricConfig {
    const maxAttempts = Math.max(
      d3.max(cells, (cell) => cell.attempts) ?? 0,
      1,
    );
    const maxMade = Math.max(d3.max(cells, (cell) => cell.made) ?? 0, 1);
    const maxMissed = Math.max(d3.max(cells, (cell) => cell.missed) ?? 0, 1);

    if (shotOutcome === "made") {
      return {
        title: "Made Shot Density",
        tooltipLabel: "Made",
        legendMinLabel: "1",
        legendMaxLabel: maxMade.toLocaleString(),
        legendNote: "Log color scale",
        palette: efficiencyPalette,
        gradient: buildGradient(efficiencyPalette),
        domain: [1, Math.max(maxMade, 2)],
        scale: "log",
        getValue: (cell) => cell.made,
        formatValue: (value) => Math.round(value).toLocaleString(),
      };
    }

    if (shotOutcome === "missed") {
      return {
        title: "Missed Shot Density",
        tooltipLabel: "Missed",
        legendMinLabel: "1",
        legendMaxLabel: maxMissed.toLocaleString(),
        legendNote: "Log color scale",
        palette: missPalette,
        gradient: buildGradient(missPalette),
        domain: [1, Math.max(maxMissed, 2)],
        scale: "log",
        getValue: (cell) => cell.missed,
        formatValue: (value) => Math.round(value).toLocaleString(),
      };
    }

    return {
      title: "Shot Density",
      tooltipLabel: "Attempts",
      legendMinLabel: "1",
      legendMaxLabel: maxAttempts.toLocaleString(),
      legendNote: "Log color scale",
      palette: volumePalette,
      gradient: buildGradient(volumePalette),
      domain: [1, Math.max(maxAttempts, 2)],
      scale: "log",
      getValue: (cell) => cell.attempts,
      formatValue: (value) => Math.round(value).toLocaleString(),
    };
  }

  function hasMetricData(cell: HeatmapCell, metricConfig: MetricConfig) {
    return metricConfig.getValue(cell) > 0;
  }

  function updateTooltipPosition(event: PointerEvent) {
    if (!container) return;

    const [x, y] = d3.pointer(event, container);
    const padding = 12;
    const tooltipWidth = 220;
    const tooltipHeight = 112;
    const preferredX = x + 16;
    const fallbackY = y + 16;
    const preferredY = y - tooltipHeight - 12;

    mousePos = {
      x: Math.min(
        Math.max(preferredX, padding),
        Math.max(padding, container.clientWidth - tooltipWidth - padding),
      ),
      y:
        preferredY >= padding
          ? preferredY
          : Math.min(
              Math.max(fallbackY, padding),
              Math.max(
                padding,
                container.clientHeight - tooltipHeight - padding,
              ),
            ),
    };
  }

  function showTooltip(event: PointerEvent, cell: HeatmapCell) {
    hoveredBin = cell;
    updateTooltipPosition(event);
  }

  function hideTooltip() {
    hoveredBin = null;
  }

  function updateSvgSize() {
    if (!chartRegion) return;

    const availableWidth = chartRegion.clientWidth;
    const availableHeight = chartRegion.clientHeight;

    if (!availableWidth || !availableHeight) return;

    const courtAspectRatio = (halfCourtWidth * 2) / halfCourtLength;
    let width = availableWidth;
    let height = width / courtAspectRatio;

    if (height > availableHeight) {
      height = availableHeight;
      width = height * courtAspectRatio;
    }

    svgRenderWidth = Math.max(Math.floor(width), 0);
    svgRenderHeight = Math.max(Math.floor(height), 0);
  }

  function fy(y: number) {
    return halfCourtLength - y;
  }

  function drawCourt(
    layer: d3.Selection<SVGGElement, unknown, null, undefined>,
  ) {
    const stroke = "#f8fafc";
    const strokeOpacity = 0.6;

    layer
      .append("rect")
      .attr("x", -halfCourtWidth)
      .attr("y", 0)
      .attr("width", halfCourtWidth * 2)
      .attr("height", halfCourtLength)
      .attr("fill", "rgba(148, 163, 184, 0.06)")
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity)
      .attr("stroke-width", 0.18);

    layer
      .append("circle")
      .attr("cx", 0)
      .attr("cy", fy(5.25))
      .attr("r", 0.75)
      .attr("fill", "none")
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity)
      .attr("stroke-width", 0.18);

    layer
      .append("line")
      .attr("x1", -3)
      .attr("x2", 3)
      .attr("y1", fy(4))
      .attr("y2", fy(4))
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity)
      .attr("stroke-width", 0.18);

    layer
      .append("rect")
      .attr("x", -8)
      .attr("y", fy(19))
      .attr("width", 16)
      .attr("height", 19)
      .attr("fill", "none")
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity)
      .attr("stroke-width", 0.18);

    layer
      .append("path")
      .attr("d", `M -6 ${fy(19)} A 6 6 0 0 0 6 ${fy(19)}`)
      .attr("fill", "none")
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity)
      .attr("stroke-width", 0.18);

    layer
      .append("path")
      .attr("d", `M -6 ${fy(19)} A 6 6 0 0 1 6 ${fy(19)}`)
      .attr("fill", "none")
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity)
      .attr("stroke-width", 0.18)
      .attr("stroke-dasharray", "0.9 0.7");

    layer
      .append("path")
      .attr("d", `M -4 ${fy(5.25)} A 4 4 0 0 0 4 ${fy(5.25)}`)
      .attr("fill", "none")
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity)
      .attr("stroke-width", 0.18);

    layer
      .append("line")
      .attr("x1", -22)
      .attr("x2", -22)
      .attr("y1", fy(0))
      .attr("y2", fy(14))
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity)
      .attr("stroke-width", 0.18);

    layer
      .append("line")
      .attr("x1", 22)
      .attr("x2", 22)
      .attr("y1", fy(0))
      .attr("y2", fy(14))
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity)
      .attr("stroke-width", 0.18);

    layer
      .append("path")
      .attr("d", `M -22 ${fy(14)} A 23.75 23.75 0 0 0 22 ${fy(14)}`)
      .attr("fill", "none")
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity)
      .attr("stroke-width", 0.18);

    layer
      .append("line")
      .attr("x1", -halfCourtWidth)
      .attr("x2", halfCourtWidth)
      .attr("y1", fy(halfCourtLength))
      .attr("y2", fy(halfCourtLength))
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity)
      .attr("stroke-width", 0.18);

    layer
      .append("circle")
      .attr("cx", 0)
      .attr("cy", fy(halfCourtLength))
      .attr("r", 6)
      .attr("fill", "none")
      .attr("stroke", stroke)
      .attr("stroke-opacity", strokeOpacity * 0.75)
      .attr("stroke-width", 0.18);
  }

  function draw() {
    if (!svgElement) return;

    const metricConfig = getMetricConfig();
    const interpolator = d3.interpolateRgbBasis(metricConfig.palette);
    const colorScale =
      metricConfig.scale === "log"
        ? d3
            .scaleSequentialLog(interpolator)
            .domain(metricConfig.domain)
            .clamp(true)
        : d3
            .scaleSequential(interpolator)
            .domain(metricConfig.domain)
            .clamp(true);

    const svg = d3.select(svgElement);
    svg.selectAll("*").remove();
    svg.attr(
      "viewBox",
      `${-halfCourtWidth} 0 ${halfCourtWidth * 2} ${halfCourtLength}`,
    );

    const courtLayer = svg.append("g").style("pointer-events", "none");
    const heatLayer = svg.append("g");

    drawCourt(courtLayer);

    heatLayer
      .selectAll("rect")
      .data(cells)
      .join("rect")
      .attr("x", (d) => d.x)
      .attr("y", (d) => fy(d.y) - cellSize)
      .attr("width", cellSize)
      .attr("height", cellSize)
      .attr("rx", 0.35)
      .attr("ry", 0.35)
      .attr("fill", (d) =>
        hasMetricData(d, metricConfig)
          ? colorScale(metricConfig.getValue(d))
          : "transparent",
      )
      .attr("fill-opacity", 0.92)
      .attr("stroke", "rgba(15, 23, 42, 0.18)")
      .attr("stroke-width", 0.08)
      .attr("pointer-events", (d) =>
        hasMetricData(d, metricConfig) ? "auto" : "none",
      )
      .on("pointerenter", function (event, d) {
        showTooltip(event, d);
        d3.select(this)
          .attr("stroke", "rgba(248, 250, 252, 0.8)")
          .attr("stroke-width", 0.2);
      })
      .on("pointermove", function (event, d) {
        showTooltip(event, d);
        d3.select(this)
          .attr("stroke", "rgba(248, 250, 252, 0.8)")
          .attr("stroke-width", 0.2);
      })
      .on("pointerleave", function () {
        hideTooltip();
        d3.select(this)
          .attr("stroke", "rgba(15, 23, 42, 0.18)")
          .attr("stroke-width", 0.08);
      });
  }

  $: metricConfig = getMetricConfig();
  $: hoveredMetricValue = hoveredBin
    ? metricConfig.formatValue(metricConfig.getValue(hoveredBin))
    : "";

  onMount(() => {
    resizeObserver = new ResizeObserver(() => {
      updateSvgSize();
    });

    if (container) resizeObserver.observe(container);
    if (chartRegion) resizeObserver.observe(chartRegion);

    updateSvgSize();

    return () => {
      resizeObserver?.disconnect();
      resizeObserver = null;
    };
  });

  $: if (chartRegion) {
    halfCourtLength;
    halfCourtWidth;
    updateSvgSize();
  }

  $: if (svgElement) {
    cells;
    shotOutcome;
    cellSize;
    halfCourtLength;
    halfCourtWidth;
    hoveredBin = null;
    draw();
  }
</script>

<div bind:this={container} class="relative h-full min-h-0 w-full">
  {#if cells.length}
    <div
      class="flex h-full min-h-0 w-full flex-col items-center justify-start gap-4 overflow-hidden rounded-3xl bg-slate-950/70 p-4"
    >
      <div class="w-full max-w-sm flex-none">
        <div
          class="rounded-2xl border border-white/10 bg-slate-900/80 px-4 py-3"
        >
          <p
            class="text-[0.7rem] font-semibold uppercase tracking-[0.22em] text-slate-400"
          >
            {metricConfig.title}
          </p>
          <div
            class="mt-3 h-3 w-full overflow-hidden rounded-full border border-white/10"
            style={`background: ${metricConfig.gradient};`}
          ></div>
          <div
            class="mt-2 flex items-center justify-between text-[0.72rem] font-medium text-slate-300"
          >
            <span>{metricConfig.legendMinLabel}</span>
            <span>{metricConfig.legendMaxLabel}</span>
          </div>
          <p
            class="mt-2 text-[0.68rem] uppercase tracking-[0.18em] text-slate-500"
          >
            {metricConfig.legendNote}
          </p>
        </div>
      </div>

      <div
        bind:this={chartRegion}
        class="flex min-h-0 w-full flex-1 items-center justify-center overflow-hidden"
      >
        <svg
          bind:this={svgElement}
          class="court-svg"
          width={svgRenderWidth}
          height={svgRenderHeight}
          preserveAspectRatio="xMidYMid meet"
        ></svg>
      </div>
    </div>

    {#if hoveredBin}
      <div
        class="pointer-events-none absolute z-20 w-[13.75rem] rounded-2xl border border-white/10 bg-slate-950/95 px-3 py-2.5 text-xs shadow-2xl shadow-slate-950/60 backdrop-blur"
        style={`left: ${mousePos.x}px; top: ${mousePos.y}px;`}
      >
        <div class="flex items-baseline justify-between gap-3">
          <p class="font-semibold text-white">{metricConfig.tooltipLabel}</p>
          <p class="text-sm font-bold text-cyan-300">{hoveredMetricValue}</p>
        </div>
        <div class="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 text-slate-300">
          <span>Attempts</span>
          <span class="text-right text-white"
            >{hoveredBin.attempts.toLocaleString()}</span
          >
          <span>Made</span>
          <span class="text-right text-white"
            >{hoveredBin.made.toLocaleString()}</span
          >
          <span>Missed</span>
          <span class="text-right text-white"
            >{hoveredBin.missed.toLocaleString()}</span
          >
          <span>FG%</span>
          <span class="text-right text-white"
            >{(hoveredBin.fgPct * 100).toFixed(1)}%</span
          >
        </div>
      </div>
    {/if}
  {:else}
    <div
      class="flex h-full min-h-[22rem] w-full items-center justify-center overflow-hidden rounded-3xl bg-slate-950/70 p-4"
    >
      <div
        class="flex h-full w-full items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-400"
      >
        No heatmap cells are available for the current filter.
      </div>
    </div>
  {/if}
</div>

<style>
  .court-svg {
    display: block;
    height: auto;
    max-height: 100%;
    width: auto;
    max-width: 100%;
    object-fit: contain;
    flex: none;
  }

  .court-svg :global(*) {
    vector-effect: non-scaling-stroke;
  }
</style>
