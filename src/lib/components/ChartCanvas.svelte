<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import {
    Chart as ChartJS,
    registerables,
    type ChartData,
    type ChartOptions,
    type ChartType,
    type Plugin,
    type UpdateMode
  } from 'chart.js';

  export let type: ChartType;
  export let data: ChartData;
  export let options: ChartOptions | undefined = undefined;
  export let plugins: Plugin[] = [];
  export let updateMode: UpdateMode | undefined = undefined;

  let canvasRef: HTMLCanvasElement;
  let chart: ChartJS | null = null;

  ChartJS.register(...registerables);

  function cloneChartValue<T>(value: T, seen = new WeakMap<object, unknown>()): T {
    if (value === null || typeof value !== 'object') return value;

    if (seen.has(value)) return seen.get(value) as T;

    if (value instanceof Date) return new Date(value) as T;

    if (Array.isArray(value)) {
      const clone: unknown[] = [];
      seen.set(value, clone);
      for (const item of value) clone.push(cloneChartValue(item, seen));
      return clone as T;
    }

    const prototype = Object.getPrototypeOf(value);
    if (prototype !== Object.prototype && prototype !== null) return value;

    const clone: Record<string, unknown> = {};
    seen.set(value, clone);

    for (const [key, item] of Object.entries(value)) {
      clone[key] = cloneChartValue(item, seen);
    }

    return clone as T;
  }

  function chartConfig() {
    return cloneChartValue({
      type,
      data,
      options,
      plugins
    });
  }

  onMount(() => {
    chart = new ChartJS(canvasRef, chartConfig());
  });

  $: if (chart) {
    chart.data = cloneChartValue(data);

    if (options) {
      chart.options = cloneChartValue(options);
    }

    chart.update(updateMode);
  }

  onDestroy(() => {
    chart?.destroy();
    chart = null;
  });
</script>

<canvas bind:this={canvasRef} {...$$restProps}></canvas>
