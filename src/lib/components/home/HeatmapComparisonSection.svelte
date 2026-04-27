<script lang="ts">
  import CourtHeatmap from "$lib/components/CourtHeatmap.svelte";
  import Scroll from "$lib/components/Scroll.svelte";
  import type { HeatmapCell, HeatmapPayload } from "$lib/types";

  export let heatmap: HeatmapPayload | null = null;
  export let seasons: string[] = [];

  let progress = 0;
  let compareStart = "2003-04";
  let compareEnd = "2023-24";

  const heatmapSteps = [
    {
      key: "rim",
      label: "Rim pressure remains",
      title: "The best shots never leave the restricted area.",
      body: "Both eras still light up near the basket. The revolution is not a rejection of layups and dunks; it is the search for cleaner ways to create them.",
    },
    {
      key: "midrange",
      label: "The middle quiets down",
      title: "The in-between floor loses its old volume.",
      body: "The mid-range used to absorb a huge number of possessions. In the modern map, that space becomes noticeably quieter.",
    },
    {
      key: "corners",
      label: "Corners grow",
      title: "Corner threes matter, but they are not the whole boom.",
      body: "The corners are valuable because the line is shorter there. They grow, but the bigger spatial change is still waiting above the break.",
    },
    {
      key: "above-break",
      label: "Above the break expands",
      title: "The arc above the break carries the modern spacing shift.",
      body: "This is where the new geometry becomes obvious: the league stretches the curved part of the arc while the middle fades.",
    },
  ] as const;

  function selectCollection<T>(
    collection: { all: T[]; bySeason: Record<string, T[]> } | null,
    season: string,
  ): T[] {
    if (!collection) return [];
    if (season === "all") return collection.all;
    return collection.bySeason[season] ?? [];
  }

  $: compareStart = seasons.includes(compareStart)
    ? compareStart
    : (seasons[0] ?? "all");
  $: compareEnd = seasons.includes(compareEnd)
    ? compareEnd
    : (seasons[seasons.length - 1] ?? "all");
  $: startCells = selectCollection<HeatmapCell>(heatmap, compareStart);
  $: endCells = selectCollection<HeatmapCell>(heatmap, compareEnd);
  $: activeStepIndex = Math.min(
    heatmapSteps.length - 1,
    Math.max(0, Math.floor((progress / 100) * heatmapSteps.length)),
  );
  $: activeStep = heatmapSteps[activeStepIndex];
  $: fadeProgress = Math.max(0, Math.min((progress - 72) / 18, 1));
</script>

<section class="order-6 mt-10">
  <Scroll bind:progress threshold={0.48} margin={8}>
    {#snippet children()}
      <div class="space-y-6">
        {#each heatmapSteps as step, index}
          <article
            class:active={activeStepIndex === index}
            class="heatmap-step panel min-h-[62vh] border border-teal-300/20 bg-slate-900/90 p-6 sm:p-8"
          >
            <p
              class="text-xs font-semibold uppercase tracking-[0.24em] text-teal-300/80"
            >
              Spatial proof
            </p>
            <h2 class="mt-3 text-2xl font-bold text-white sm:text-3xl">
              {step.title}
            </h2>
            <p class="mt-4 text-sm leading-7 text-slate-300">{step.body}</p>
            <div
              class="mt-6 rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4"
            >
              <p
                class="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400"
              >
                Focus
              </p>
              <p class="mt-2 text-xl font-bold text-white">{step.label}</p>
              <p class="mt-1 text-sm text-slate-400">
                {compareStart} versus {compareEnd}
              </p>
            </div>
          </article>
        {/each}
      </div>
    {/snippet}

    {#snippet viz()}
      <article
        class="panel overflow-hidden border border-emerald-300/20 bg-slate-900/90"
      >
        <div class="border-b border-white/10 px-6 py-5 lg:px-8">
          <div
            class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between"
          >
            <div>
              <p
                class="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-300/80"
              >
                Scene 2
              </p>
              <h3 class="mt-2 text-2xl font-bold text-white">
                Guided heatmap comparison
              </h3>
              <p class="mt-2 text-sm leading-6 text-slate-400">
                {activeStep.label}: {fadeProgress < 0.5
                  ? "all-shot volume"
                  : "made-shot density"}
              </p>
            </div>

            <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
              <label class="flex items-center gap-3 text-sm text-slate-300">
                <span
                  class="font-semibold uppercase tracking-[0.18em] text-slate-400"
                  >Before</span
                >
                <select
                  class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-emerald-400/60"
                  bind:value={compareStart}
                >
                  {#each seasons as season}
                    <option value={season}>{season}</option>
                  {/each}
                </select>
              </label>

              <label class="flex items-center gap-3 text-sm text-slate-300">
                <span
                  class="font-semibold uppercase tracking-[0.18em] text-slate-400"
                  >After</span
                >
                <select
                  class="rounded-xl border border-white/10 bg-slate-950/90 px-4 py-2 text-sm text-white outline-none transition focus:border-emerald-400/60"
                  bind:value={compareEnd}
                >
                  {#each seasons as season}
                    <option value={season}>{season}</option>
                  {/each}
                </select>
              </label>
            </div>
          </div>
        </div>

        <div class="grid gap-4 px-4 py-5 lg:grid-cols-2 lg:px-6 lg:py-6">
          {#each [{ label: "Before", season: compareStart, cells: startCells }, { label: "After", season: compareEnd, cells: endCells }] as comparison}
            <div class="rounded-3xl border border-white/10 bg-slate-950/50 p-3">
              <div class="mb-3 flex items-center justify-between gap-3 px-2">
                <div>
                  <p
                    class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400"
                  >
                    {comparison.label}
                  </p>
                  <p class="mt-1 text-xl font-bold text-white">
                    {comparison.season}
                  </p>
                </div>
                <p
                  class="rounded-full border border-white/10 bg-slate-900/90 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-emerald-200"
                >
                  {fadeProgress < 0.5 ? "All shots" : "Made shots"}
                </p>
              </div>

              <div
                class={`heatmap-frame spotlight-${activeStep.key} grid min-h-[28rem]`}
              >
                <div
                  class="col-start-1 row-start-1 h-full transition-opacity duration-500"
                  style={`opacity: ${1 - fadeProgress}; pointer-events: ${fadeProgress < 0.98 ? "auto" : "none"}; z-index: ${fadeProgress < 0.98 ? 20 : 10};`}
                >
                  <CourtHeatmap
                    cells={comparison.cells}
                    shotOutcome="all"
                    cellSize={heatmap?.metadata.cellSize ?? 2}
                    halfCourtLength={heatmap?.metadata.halfCourtLength ?? 47}
                    halfCourtWidth={heatmap?.metadata.halfCourtWidth ?? 25}
                  />
                </div>

                <div
                  class="col-start-1 row-start-1 h-full transition-opacity duration-500"
                  style={`opacity: ${fadeProgress}; pointer-events: ${fadeProgress >= 0.98 ? "auto" : "none"}; z-index: ${fadeProgress >= 0.98 ? 20 : 10};`}
                >
                  <CourtHeatmap
                    cells={comparison.cells}
                    shotOutcome="made"
                    cellSize={heatmap?.metadata.cellSize ?? 2}
                    halfCourtLength={heatmap?.metadata.halfCourtLength ?? 47}
                    halfCourtWidth={heatmap?.metadata.halfCourtWidth ?? 25}
                  />
                </div>
                <div
                  class={`court-spotlight ${activeStep.key}`}
                  aria-hidden="true"
                ></div>
              </div>
            </div>
          {/each}
        </div>
      </article>
    {/snippet}
  </Scroll>
</section>

<style>
  .heatmap-step {
    transition:
      border-color 220ms ease,
      opacity 220ms ease,
      transform 220ms ease;
  }

  .heatmap-step:not(.active) {
    opacity: 0.68;
  }

  .heatmap-step.active {
    border-color: rgba(45, 212, 191, 0.42);
    transform: translateY(-2px);
  }

  .heatmap-frame {
    position: relative;
  }

  .court-spotlight {
    pointer-events: none;
    position: absolute;
    z-index: 30;
    border: 2px solid rgba(253, 230, 138, 0.9);
    background: rgba(253, 230, 138, 0.09);
    box-shadow:
      0 0 0 999px rgba(2, 6, 23, 0.18),
      0 0 32px rgba(251, 191, 36, 0.34);
    transition:
      inset 260ms ease,
      width 260ms ease,
      height 260ms ease,
      border-radius 260ms ease;
  }

  .court-spotlight.rim {
    left: 38%;
    bottom: 6%;
    width: 24%;
    height: 18%;
    border-radius: 1rem 1rem 999px 999px;
  }

  .court-spotlight.midrange {
    left: 24%;
    bottom: 8%;
    width: 52%;
    height: 36%;
    border-radius: 1.25rem 1.25rem 999px 999px;
  }

  .court-spotlight.corners {
    left: 7%;
    bottom: 2%;
    width: 20%;
    height: 32%;
    border-radius: 1rem;
  }

  .court-spotlight.corners::after {
    content: "";
    position: absolute;
    right: -330%;
    bottom: -2px;
    width: 100%;
    height: calc(100% + 4px);
    border: 2px solid rgba(253, 230, 138, 0.9);
    border-radius: 1rem;
    background: rgba(253, 230, 138, 0.09);
    box-shadow: 0 0 32px rgba(251, 191, 36, 0.34);
  }

  .court-spotlight.above-break {
    left: 20%;
    bottom: 14%;
    width: 60%;
    height: 42%;
    border-radius: 999px 999px 1.25rem 1.25rem;
  }
</style>
