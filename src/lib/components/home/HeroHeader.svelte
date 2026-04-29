<script lang="ts">
  import type { StoryMetric } from '$lib/content/shotEvolutionStory';
  
  type Definition = {
    key: string;
    label: string;
    definition: string;
    read_more?: string;
  };

  type ShotDot = {
    x: number;
    y: number;
    size: number;
    tone: 'rim' | 'mid' | 'arc' | 'corner';
    delay: number;
  };

  const shotDots: ShotDot[] = [
    { x: 49, y: 78, size: 6, tone: 'rim', delay: 0 },
    { x: 52, y: 74, size: 4, tone: 'rim', delay: 0.4 },
    { x: 46, y: 71, size: 5, tone: 'rim', delay: 0.8 },
    { x: 55, y: 69, size: 4, tone: 'rim', delay: 1.2 },
    { x: 42, y: 66, size: 3, tone: 'rim', delay: 1.6 },
    { x: 58, y: 63, size: 3, tone: 'rim', delay: 2.0 },
    { x: 36, y: 55, size: 4, tone: 'mid', delay: 0.2 },
    { x: 45, y: 51, size: 3, tone: 'mid', delay: 0.7 },
    { x: 54, y: 49, size: 4, tone: 'mid', delay: 1.1 },
    { x: 63, y: 55, size: 3, tone: 'mid', delay: 1.5 },
    { x: 31, y: 43, size: 3, tone: 'mid', delay: 1.9 },
    { x: 69, y: 43, size: 3, tone: 'mid', delay: 2.3 },
    { x: 18, y: 68, size: 5, tone: 'corner', delay: 0.1 },
    { x: 15, y: 61, size: 4, tone: 'corner', delay: 0.9 },
    { x: 82, y: 68, size: 5, tone: 'corner', delay: 1.7 },
    { x: 85, y: 61, size: 4, tone: 'corner', delay: 2.5 },
    { x: 20, y: 54, size: 3, tone: 'corner', delay: 3.1 },
    { x: 80, y: 54, size: 3, tone: 'corner', delay: 3.7 },
    { x: 28, y: 31, size: 5, tone: 'arc', delay: 0.3 },
    { x: 35, y: 23, size: 4, tone: 'arc', delay: 0.8 },
    { x: 44, y: 18, size: 5, tone: 'arc', delay: 1.3 },
    { x: 51, y: 16, size: 6, tone: 'arc', delay: 1.8 },
    { x: 59, y: 19, size: 5, tone: 'arc', delay: 2.2 },
    { x: 67, y: 24, size: 4, tone: 'arc', delay: 2.7 },
    { x: 73, y: 32, size: 5, tone: 'arc', delay: 3.2 },
    { x: 23, y: 38, size: 3, tone: 'arc', delay: 3.6 },
    { x: 77, y: 38, size: 3, tone: 'arc', delay: 4.1 },
    { x: 39, y: 34, size: 3, tone: 'arc', delay: 4.5 },
    { x: 61, y: 34, size: 3, tone: 'arc', delay: 4.9 }
  ];

  export let metrics: StoryMetric[] = [];
  const definitions: Definition[] = [
    {
      key: 'three_point_line',
      label: 'Three-point line',
      definition:
        'The arc where shots become worth three points instead of two. It is 22 feet in the corners and 23.75 feet above the break.',
      read_more: 'https://en.wikipedia.org/wiki/Three-point_field_goal'
    },
    {
      key: 'rim',
      label: 'Rim',
      definition: 'The metal hoop attached to the backboard, 10 feet above the playing surface, through which players attempt to score.',
    },
    {
      key: 'midrange',
      label: 'Mid-range',
      definition:
        'The area inside the three-point arc but away from the rim; historically common but less favored in modern offenses.',
      read_more: 'https://www.breakthroughbasketball.com/training/midrange-mastery'
    },
    {
      key: 'field_goal_percentage',
      label: 'Field goal percentage',
      definition: 'The ratio of made shots to attempted shots, expressed as a percentage.',
      read_more: 'https://jr.nba.com/field-goal-percentage-fg/'
    },
    {
      key: 'attempts',
      label: 'Attempts',
      definition: 'The total number of shot attempts from a location or player.',
    },
    {
      key: 'season',
      label: 'Season',
      definition:
        'An NBA year, usually written across two calendar years, such as 2023-24. The regular season typically runs from October to April.',
      read_more: 'https://en.wikipedia.org/wiki/2025%E2%80%9326_NBA_season'
    },
    {
      key: 'above_the_break',
      label: 'Above the break',
      definition:
        'Three-point shots taken from anywhere other than the corners. These shots are farther from the basket than corner threes.',
      read_more: 'https://abovethebreak.substack.com/p/whats-winning-in-the-nba-playoffs'
    }
  ];
</script>

<header class="shot-hero relative isolate min-h-screen overflow-hidden">
  <div class="court-backdrop absolute inset-0" aria-hidden="true">
    <div class="hardwood"></div>
    <div class="court-lines">
      <div class="baseline"></div>
      <div class="sideline left"></div>
      <div class="sideline right"></div>
      <div class="paint"></div>
      <div class="free-throw"></div>
      <div class="rim"></div>
      <div class="restricted"></div>
      <div class="arc"></div>
      <div class="corner left"></div>
      <div class="corner right"></div>
      <div class="center-line"></div>
    </div>
  </div>

  <div class="absolute inset-0 bg-slate-950/38" aria-hidden="true"></div>
  <div class="absolute inset-0 bg-[linear-gradient(90deg,rgba(2,6,23,0.95)_0%,rgba(2,6,23,0.82)_34%,rgba(2,6,23,0.42)_68%,rgba(2,6,23,0.76)_100%)]" aria-hidden="true"></div>
  <div class="shot-field absolute inset-0" aria-hidden="true">
    {#each shotDots as dot}
      <span
        class={`shot-dot ${dot.tone}`}
        style={`left: ${dot.x}%; top: ${dot.y}%; width: ${dot.size}px; height: ${dot.size}px; animation-delay: ${dot.delay}s;`}
      ></span>
    {/each}
    <div class="data-trace trace-one"></div>
    <div class="data-trace trace-two"></div>
  </div>

  <div class="relative z-10 mx-auto flex max-w-[118rem] flex-col justify-center px-5 py-20 sm:px-8 lg:px-12">
    <div class="max-w-5xl">
      <p class="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300/90 sm:text-sm">
        NBA Shot Evolution
      </p>
      <h1 class="mt-5 max-w-5xl text-4xl font-black leading-[0.98] tracking-tight text-white sm:text-6xl lg:text-7xl">
        The NBA Didn&apos;t Just Move Back. It Gave Up the Middle.
      </h1>
      <p class="mt-6 max-w-3xl text-base leading-8 text-slate-200 sm:text-lg">
        From 2003-04 through 2023-24, millions of attempts show a league rewiring itself. Fewer possessions ending
        in the mid-range space, more pressure at the rim, and a much larger share of shots launched above the arc.
      </p>
      <p class="mt-4 max-w-3xl text-xs italic leading-5 text-slate-400 sm:text-sm">
        Note: Data from the 2020-21 season may show irregular patterns due to the COVID-19 pandemic and schedule disruption.
      </p>

      {#if metrics.length}
        <div class="mt-9 grid max-w-6xl gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {#each metrics as metric}
            <div class={`metric-card ${metric.tone}`}>
              <p class="text-[0.68rem] font-semibold uppercase tracking-[0.2em] text-slate-400">{metric.label}</p>
              <p class="mt-2 text-xl font-black text-white sm:text-2xl">{metric.value}</p>
              <p class="mt-2 text-xs leading-5 text-slate-300">{metric.detail}</p>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <div class="mt-8 max-w-6xl">
      <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">Definitions</p>
      <div class="mt-3 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
        {#each definitions as def}
          <div class="rounded-xl border border-white/10 bg-slate-950/72 p-3 text-sm text-slate-200 shadow-lg shadow-slate-950/20 backdrop-blur">
            <div class="flex items-start justify-between gap-3">
              <p class="font-semibold text-white">{def.label}</p>
              {#if def.read_more}
                <a
                  href={def.read_more}
                  class="shrink-0 text-[0.62rem] font-bold uppercase tracking-[0.14em] text-amber-200 underline decoration-amber-400/40 underline-offset-4"
                  target="_blank"
                  rel="noreferrer"
                >
                  More
                </a>
              {/if}
            </div>
            <p class="mt-1 line-clamp-3 text-xs leading-5 text-slate-300">{def.definition}</p>
          </div>
        {/each}
      </div>
    </div>

    

    <div class="absolute bottom-8 left-5 right-5 z-10 mx-auto flex max-w-[118rem] items-center justify-between gap-6 px-0 text-xs font-semibold uppercase tracking-[0.22em] text-slate-300 sm:left-8 sm:right-8 lg:left-12 lg:right-12">
      <span class="hidden h-px flex-1 bg-gradient-to-r from-amber-300/45 via-teal-300/30 to-transparent sm:block"></span>
      <span class="scroll-cue">Scroll to explore</span>
    </div>
  </div>
</header>

<style>
  .shot-hero {
    background: #020617;
  }

  .court-backdrop {
    overflow: hidden;
    background:
      radial-gradient(circle at 50% 70%, rgba(251, 191, 36, 0.22), transparent 22%),
      radial-gradient(circle at 68% 24%, rgba(20, 184, 166, 0.18), transparent 20%),
      linear-gradient(180deg, rgba(15, 23, 42, 0.18), rgba(2, 6, 23, 0.92));
  }

  .hardwood {
    position: absolute;
    inset: -6rem -4rem;
    opacity: 0.5;
    background:
      linear-gradient(90deg, rgba(251, 191, 36, 0.05) 0 1px, transparent 1px 11%),
      linear-gradient(180deg, rgba(255, 255, 255, 0.035) 0 1px, transparent 1px 5rem),
      repeating-linear-gradient(90deg, rgba(120, 53, 15, 0.28) 0 8rem, rgba(146, 64, 14, 0.2) 8rem 16rem);
    transform: perspective(54rem) rotateX(58deg) translateY(10rem) scale(1.25);
    transform-origin: bottom center;
  }

  .court-lines {
    position: absolute;
    left: max(2rem, 44vw);
    right: min(2rem, 5vw);
    bottom: -3rem;
    height: min(82vh, 56rem);
    opacity: 0.76;
    transform: perspective(54rem) rotateX(56deg);
    transform-origin: bottom center;
  }

  .court-lines > div {
    position: absolute;
    border-color: rgba(248, 250, 252, 0.34);
  }

  .baseline {
    left: 4%;
    right: 4%;
    bottom: 8%;
    border-bottom: 2px solid;
  }

  .sideline {
    bottom: 8%;
    height: 88%;
    border-left: 2px solid;
  }

  .sideline.left {
    left: 4%;
  }

  .sideline.right {
    right: 4%;
  }

  .paint {
    left: 38%;
    bottom: 8%;
    width: 24%;
    height: 36%;
    border: 2px solid;
    background: rgba(15, 23, 42, 0.16);
  }

  .free-throw {
    left: 36%;
    bottom: 37%;
    width: 28%;
    height: 17%;
    border: 2px solid;
    border-bottom: 0;
    border-radius: 50% 50% 0 0;
  }

  .rim {
    left: calc(50% - 1.25rem);
    bottom: 19%;
    width: 2.5rem;
    height: 2.5rem;
    border: 3px solid rgba(251, 191, 36, 0.72);
    border-radius: 999px;
    box-shadow: 0 0 24px rgba(251, 191, 36, 0.32);
  }

  .restricted {
    left: 42%;
    bottom: 16%;
    width: 16%;
    height: 16%;
    border: 2px solid;
    border-bottom: 0;
    border-radius: 50% 50% 0 0;
  }

  .arc {
    left: 14%;
    bottom: 10%;
    width: 72%;
    height: 78%;
    border: 3px solid rgba(45, 212, 191, 0.44);
    border-bottom: 0;
    border-radius: 50% 50% 0 0;
    box-shadow: 0 -18px 54px rgba(20, 184, 166, 0.12);
  }

  .corner {
    bottom: 8%;
    height: 43%;
    border-left: 3px solid rgba(45, 212, 191, 0.44);
  }

  .corner.left {
    left: 17%;
  }

  .corner.right {
    right: 17%;
  }

  .center-line {
    left: 4%;
    right: 4%;
    top: 5%;
    border-top: 1px solid rgba(248, 250, 252, 0.16);
  }

  .shot-field {
    z-index: 5;
    pointer-events: none;
    mix-blend-mode: screen;
  }

  .shot-dot {
    position: absolute;
    border-radius: 999px;
    opacity: 0.92;
    animation: pulse-shot 5.8s ease-in-out infinite;
    will-change: transform, opacity;
  }

  .shot-dot.rim {
    background: #fde68a;
    box-shadow: 0 0 18px rgba(253, 230, 138, 0.8);
  }

  .shot-dot.mid {
    background: #fb923c;
    box-shadow: 0 0 14px rgba(251, 146, 60, 0.54);
    opacity: 0.54;
  }

  .shot-dot.arc,
  .shot-dot.corner {
    background: #2dd4bf;
    box-shadow: 0 0 22px rgba(45, 212, 191, 0.82);
  }

  .shot-dot.corner {
    background: #38bdf8;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.76);
  }

  .data-trace {
    position: absolute;
    height: 1px;
    opacity: 0.34;
    transform-origin: left center;
  }

  .trace-one {
    left: 39%;
    top: 35%;
    width: 38%;
    background: linear-gradient(90deg, transparent, rgba(45, 212, 191, 0.9), transparent);
    transform: rotate(17deg);
  }

  .trace-two {
    left: 48%;
    top: 24%;
    width: 26%;
    background: linear-gradient(90deg, transparent, rgba(251, 191, 36, 0.86), transparent);
    transform: rotate(-22deg);
  }

  .scroll-cue {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    color: rgba(226, 232, 240, 0.86);
  }

  .metric-card {
    border: 1px solid rgba(255, 255, 255, 0.11);
    border-radius: 1.25rem;
    background: rgba(2, 6, 23, 0.68);
    padding: 1rem;
    box-shadow: 0 1rem 2.5rem rgba(2, 6, 23, 0.28);
    backdrop-filter: blur(14px);
  }

  .metric-card.amber {
    border-color: rgba(251, 191, 36, 0.28);
  }

  .metric-card.teal {
    border-color: rgba(45, 212, 191, 0.28);
  }

  .metric-card.orange {
    border-color: rgba(251, 146, 60, 0.28);
  }

  .metric-card.sky {
    border-color: rgba(56, 189, 248, 0.28);
  }

  .scroll-cue::after {
    content: '';
    width: 0.55rem;
    height: 0.55rem;
    border-right: 2px solid rgba(251, 191, 36, 0.9);
    border-bottom: 2px solid rgba(251, 191, 36, 0.9);
    transform: rotate(45deg);
    animation: cue-drop 1.6s ease-in-out infinite;
  }

  @keyframes pulse-shot {
    0%,
    100% {
      transform: scale(1);
      opacity: 0.86;
    }

    50% {
      transform: scale(1.28);
      opacity: 1;
    }
  }

  @keyframes cue-drop {
    0%,
    100% {
      transform: translateY(-2px) rotate(45deg);
      opacity: 0.45;
    }

    50% {
      transform: translateY(4px) rotate(45deg);
      opacity: 1;
    }
  }

  @media (max-width: 768px) {
    .court-lines {
      left: 4vw;
      right: 4vw;
      bottom: -7rem;
      height: 58vh;
      opacity: 0.52;
    }

    .shot-dot {
      opacity: 0.7;
    }

    .shot-dot:nth-child(3n) {
      display: none;
    }

    .hardwood {
      opacity: 0.38;
      transform: perspective(42rem) rotateX(60deg) translateY(11rem) scale(1.18);
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .shot-dot,
    .scroll-cue::after {
      animation: none;
    }
  }
</style>
