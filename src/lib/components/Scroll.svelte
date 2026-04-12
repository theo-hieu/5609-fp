<!-- mainly inspired by https://github.com/LeaVerou/svelte-scrolly/blob/main/Scrolly.svelte -->
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { onMount } from 'svelte';

  type Props = {
    progress?: number;
    progressRaw?: number;
    threshold?: number;
    margin?: number;
    debounce?: number | boolean;
    throttle?: number | boolean;
    layout?: 'story-first' | 'viz-first' | 'overlap';
    storyWidth?: string;
    vizWidth?: string;
    gap?: string;
    children?: Snippet;
    viz?: Snippet;
  };

  let {
    progress = $bindable(),
    progressRaw,
    threshold = 0.5,
    margin = 30,
    debounce = false,
    throttle = false,
    layout = 'story-first',
    storyWidth = '1fr',
    vizWidth = '1fr',
    gap = '4rem',
    children,
    viz
  }: Props = $props();

  let container: HTMLElement;
  let minTop: number;
  let maxTop: number;
  let pageTop: number;
  let rect: DOMRect;
  let intersectionObserver: IntersectionObserver;
  let resizeObserver: ResizeObserver;

  const clamp = (min: number, value: number, max: number) => Math.min(Math.max(min, value), max);
  const getProgress = (value: number, min: number, max: number) => (100 * (value - min)) / (max - min);
  const runImmediately = (fn: () => void) => fn();
  const identity = (fn: () => void) => fn;

  let last = 0;
  let throttled = $derived(
    (throttle as number) > 0
      ? function (fn: () => void) {
          return function () {
            const now = performance.now();
            if (now - last >= (throttle as number)) {
              fn();
              last = now;
            }
          };
        }
      : identity
  );

  let debouncerId: number;
  let debounced = $derived(
    debounce
      ? (debounce as number) > 0
        ? function (fn: () => void) {
            clearTimeout(debouncerId);
            debouncerId = window.setTimeout(fn, debounce as number);
          }
        : function (fn: () => void) {
            cancelAnimationFrame(debouncerId);
            debouncerId = requestAnimationFrame(fn);
          }
      : runImmediately
  );

  onMount(() => {
    function calculateProgress({ top = container.getBoundingClientRect().top }: { top?: number } = {}): void {
      progressRaw = getProgress(top, minTop, maxTop);
      updateProgress();
    }

    function updateProgress() {
      const clampedProgress = clamp(0, progressRaw as number, 100);

      if (clampedProgress === 0 || clampedProgress === 100) {
        progress = clampedProgress;
      } else {
        debounced(throttled(() => (progress = clampedProgress)));
      }
    }

    function calculateBounds() {
      rect = container.getBoundingClientRect();
      pageTop = window.scrollY + rect.top;
      minTop = Math.min(pageTop, innerHeight * threshold) + margin;
      maxTop = innerHeight - rect.height + margin;
      calculateProgress(rect);
    }

    const handleScroll = () => calculateProgress();
    const handleResize = () => calculateBounds();

    function enableTracking() {
      calculateBounds();
      calculateProgress();
      window.addEventListener('scroll', handleScroll);
      window.addEventListener('resize', handleResize);
      resizeObserver?.observe(container);
    }

    function disableTracking() {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', handleResize);
      resizeObserver?.unobserve(container);
    }

    intersectionObserver = new IntersectionObserver((entries) => {
      const lastEntry = entries.at(-1);
      if (!lastEntry) return;

      if (lastEntry.isIntersecting) {
        enableTracking();
      } else {
        disableTracking();
      }
    });

    resizeObserver = new ResizeObserver(calculateBounds);
    intersectionObserver.observe(container);
    calculateBounds();

    return () => {
      disableTracking();
      intersectionObserver.disconnect();
      resizeObserver.disconnect();
    };
  });
</script>

<section
  class="scrolly"
  bind:this={container}
  style="--scrolly-margin: {margin}; --scrolly-layout: {layout}; --scrolly-story-width: {storyWidth}; --scrolly-viz-width: {vizWidth}; --scrolly-gap: {gap}"
>
  <section class="story">
    {@render children?.()}
  </section>
  <section class="viz">
    {@render viz?.()}
  </section>
</section>

<style>
  .scrolly {
    container-type: inline-size;
    position: relative;
    display: grid;
    grid-template-columns: var(--scrolly-story-width, 1fr) var(--scrolly-viz-width, 1fr);
    grid-auto-flow: row dense;
    gap: var(--scrolly-gap, 4rem);
  }

  .viz,
  .story {
    grid-row: 1;
  }

  .viz {
    position: sticky;
    top: max(calc(var(--scrolly-margin, 0) * 1px), var(--scrolly-viz-top, 2em));
    max-height: 100vh;
  }

  @container style(--scrolly-layout: viz-first) {
    .scrolly {
      grid-template-columns: var(--scrolly-viz-width, 1fr) var(--scrolly-story-width, 1fr);
    }

    .viz {
      grid-column: 1;
    }

    .story {
      grid-column: 2;
    }
  }

  @container style(--scrolly-layout: overlap) {
    .scrolly {
      grid-template-columns: 1fr;
    }

    .viz,
    .story {
      grid-column: 1;
    }
  }

  @media (max-width: 1023px) {
    .scrolly {
      grid-template-columns: 1fr;
    }

    .viz,
    .story {
      grid-column: 1;
      grid-row: auto;
    }

    .viz {
      position: relative;
      top: auto;
      max-height: none;
      order: -1;
    }
  }
</style>
