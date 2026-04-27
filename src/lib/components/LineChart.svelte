<script lang="ts">
  import ChartCanvas from '$lib/components/ChartCanvas.svelte';
  import {
    CategoryScale,
    Chart as ChartJS,
    Filler,
    Legend,
    LineElement,
    LinearScale,
    PointElement,
    Title,
    Tooltip,
    type ChartData,
    type ChartOptions
  } from 'chart.js';

  import type { MonthlyTrend, ShotOutcome } from '$lib/types';

  export let data: MonthlyTrend[] = [];
  export let shotOutcome: ShotOutcome = 'all';
  export let metric: 'volume' | 'rate' = 'volume';

  ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

  function compactMonthLabel(value: string) {
    const [year, month] = value.split('-').map(Number);
    const date = new Date(year, month - 1, 1);
    return date.toLocaleString('en-US', { month: 'short', year: '2-digit' });
  }

  function volumeValue(row: MonthlyTrend) {
    if (shotOutcome === 'made') return row.made;
    if (shotOutcome === 'missed') return row.missed;
    return row.attempts;
  }

  function rateValue(row: MonthlyTrend) {
    if (shotOutcome === 'missed') return row.attempts ? row.missed / row.attempts : 0;
    return row.fgPct;
  }

  $: labels = data.map((row) => compactMonthLabel(row.month));
  $: points = data.map((row) => (metric === 'volume' ? volumeValue(row) : +(rateValue(row) * 100).toFixed(1)));
  $: datasetLabel =
    metric === 'volume'
      ? shotOutcome === 'all'
        ? 'Shot Attempts'
        : shotOutcome === 'made'
          ? 'Made Shots'
          : 'Missed Shots'
      : shotOutcome === 'missed'
        ? 'Miss Rate'
        : 'Field Goal Rate';
  $: strokeColor =
    metric === 'volume'
      ? shotOutcome === 'missed'
        ? '#fb923c'
        : shotOutcome === 'made'
          ? '#2dd4bf'
          : '#fbbf24'
      : shotOutcome === 'missed'
        ? '#f97316'
        : '#14b8a6';
  $: fillColor =
    metric === 'volume'
      ? shotOutcome === 'missed'
        ? 'rgba(249, 115, 22, 0.18)'
        : shotOutcome === 'made'
          ? 'rgba(45, 212, 191, 0.18)'
          : 'rgba(251, 191, 36, 0.18)'
      : shotOutcome === 'missed'
        ? 'rgba(249, 115, 22, 0.14)'
        : 'rgba(20, 184, 166, 0.14)';

  $: chartData = {
    labels,
    datasets: [
      {
        label: datasetLabel,
        data: points,
        borderColor: strokeColor,
        backgroundColor: fillColor,
        fill: true,
        tension: 0.28,
        pointRadius: points.length > 40 ? 0 : 2.5,
        pointHoverRadius: 4,
        borderWidth: 2.25
      }
    ]
  } satisfies ChartData<'line'>;

  $: options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(2, 6, 23, 0.95)',
        borderColor: 'rgba(148, 163, 184, 0.18)',
        borderWidth: 1,
        callbacks: {
          label: (context) =>
            metric === 'volume'
              ? `${datasetLabel}: ${Number(context.raw).toLocaleString()}`
              : `${datasetLabel}: ${Number(context.raw).toFixed(1)}%`
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#94a3b8',
          autoSkip: true,
          maxTicksLimit: 10
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.09)'
        }
      },
      y: {
        ticks: {
          color: '#cbd5e1',
          callback: (value) => (metric === 'volume' ? Number(value).toLocaleString() : `${value}%`)
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.09)'
        }
      }
    }
  } satisfies ChartOptions<'line'>;
</script>

<div class="h-[22rem] lg:h-[28rem]">
  {#if data.length}
    <ChartCanvas type="line" data={chartData} {options} />
  {:else}
    <div class="flex h-full items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-400">
      No monthly trend data is available for the current filter.
    </div>
  {/if}
</div>
