<script lang="ts">
  import { Chart } from 'svelte-chartjs';
  import {
    BarElement,
    BarController,
    CategoryScale,
    Chart as ChartJS,
    Legend,
    LineElement,
    LineController,
    LinearScale,
    PointElement,
    Title,
    Tooltip,
    type ChartData,
    type ChartOptions
  } from 'chart.js';

  import type { DistanceBucket, ShotOutcome } from '$lib/types';

  export let data: DistanceBucket[] = [];
  export let shotOutcome: ShotOutcome = 'all';
  export let longDistanceBucket = 40;

  ChartJS.register(
    CategoryScale,
    LinearScale,
    BarController,
    BarElement,
    LineController,
    LineElement,
    PointElement,
    Title,
    Tooltip,
    Legend
  );

  function makeRate(row: DistanceBucket) {
    if (shotOutcome === 'missed') return row.attempts ? row.missed / row.attempts : 0;
    return row.fgPct;
  }

  function makeVolume(row: DistanceBucket) {
    if (shotOutcome === 'made') return row.made;
    if (shotOutcome === 'missed') return row.missed;
    return row.attempts;
  }

  function labelBucket(bucket: number) {
    if (bucket >= longDistanceBucket) return `${longDistanceBucket}+ ft`;
    return `${bucket}-${bucket + 1} ft`;
  }

  $: labels = data.map((row) => labelBucket(row.distanceBucket));
  $: ratePoints = data.map((row) => +(makeRate(row) * 100).toFixed(1));
  $: volumePoints = data.map((row) => makeVolume(row));
  $: rateLabel = shotOutcome === 'missed' ? 'Miss Rate' : 'Field Goal Rate';
  $: volumeLabel =
    shotOutcome === 'all' ? 'Shot Attempts' : shotOutcome === 'made' ? 'Made Shots' : 'Missed Shots';
  $: chartData = {
    labels,
    datasets: [
      {
        type: 'bar',
        label: rateLabel,
        data: ratePoints,
        backgroundColor: ratePoints.map((value) =>
          shotOutcome === 'missed'
            ? value >= 60
              ? 'rgba(249, 115, 22, 0.82)'
              : value >= 45
                ? 'rgba(251, 191, 36, 0.78)'
                : 'rgba(34, 197, 94, 0.72)'
            : value >= 55
              ? 'rgba(20, 184, 166, 0.82)'
              : value >= 40
                ? 'rgba(251, 191, 36, 0.78)'
                : 'rgba(249, 115, 22, 0.78)'
        ),
        borderRadius: 8,
        yAxisID: 'rate'
      },
      {
        type: 'line',
        label: volumeLabel,
        data: volumePoints,
        borderColor: '#f8fafc',
        backgroundColor: 'rgba(248, 250, 252, 0.14)',
        tension: 0.28,
        pointRadius: 3,
        pointHoverRadius: 4,
        borderWidth: 2.1,
        yAxisID: 'volume'
      }
    ]
  } satisfies ChartData<'bar' | 'line'>;

  $: options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        labels: {
          color: '#e2e8f0'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(2, 6, 23, 0.95)',
        borderColor: 'rgba(148, 163, 184, 0.18)',
        borderWidth: 1,
        callbacks: {
          label: (context) =>
            context.dataset.type === 'bar'
              ? `${rateLabel}: ${Number(context.raw).toFixed(1)}%`
              : `${volumeLabel}: ${Number(context.raw).toLocaleString()}`
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#94a3b8',
          maxRotation: 0,
          autoSkip: true
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.08)'
        }
      },
      rate: {
        type: 'linear',
        position: 'left',
        suggestedMax: 100,
        ticks: {
          color: '#fbbf24',
          callback: (value) => `${value}%`
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.08)'
        }
      },
      volume: {
        type: 'linear',
        position: 'right',
        ticks: {
          color: '#e2e8f0',
          callback: (value) => Number(value).toLocaleString()
        },
        grid: {
          drawOnChartArea: false
        }
      }
    }
  } satisfies ChartOptions<'bar' | 'line'>;
</script>

<div class="h-full min-h-[20rem]">
  {#if data.length}
    <Chart type="bar" data={chartData} {options} />
  {:else}
    <div class="flex h-full items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-400">
      No distance profile data is available for the current filter.
    </div>
  {/if}
</div>
