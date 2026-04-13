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
  export let highlightThreePointRange = false;

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

  function baseRateColor(value: number) {
    if (shotOutcome === 'missed') {
      if (value >= 60) return '249, 115, 22';
      if (value >= 45) return '251, 191, 36';
      return '34, 197, 94';
    }

    if (value >= 55) return '20, 184, 166';
    if (value >= 40) return '251, 191, 36';
    return '249, 115, 22';
  }

  function inThreePointRange(bucket: number) {
    return bucket >= 22;
  }

  $: labels = data.map((row) => labelBucket(row.distanceBucket));
  $: ratePoints = data.map((row) => +(makeRate(row) * 100).toFixed(1));
  $: volumePoints = data.map((row) => makeVolume(row));
  $: rateLabel = shotOutcome === 'missed' ? 'Miss Rate' : 'Field Goal Rate';
  $: volumeLabel =
    shotOutcome === 'all' ? 'Shot Attempts' : shotOutcome === 'made' ? 'Made Shots' : 'Missed Shots';
  $: highlightedBuckets = data.map((row) => inThreePointRange(row.distanceBucket));
  $: chartData = {
    labels,
    datasets: [
      {
        type: 'bar',
        label: rateLabel,
        data: ratePoints,
        backgroundColor: ratePoints.map((value, index) => {
          const alpha = highlightThreePointRange ? (highlightedBuckets[index] ? 0.92 : 0.22) : 0.82;
          return `rgba(${baseRateColor(value)}, ${alpha})`;
        }),
        borderColor: ratePoints.map((value, index) => {
          const alpha = highlightThreePointRange ? (highlightedBuckets[index] ? 0.95 : 0.12) : 0;
          return `rgba(${baseRateColor(value)}, ${alpha})`;
        }),
        borderWidth: highlightThreePointRange ? 1.2 : 0,
        borderRadius: 8,
        yAxisID: 'rate'
      },
      {
        type: 'line',
        label: volumeLabel,
        data: volumePoints,
        borderColor: highlightThreePointRange ? 'rgba(248, 250, 252, 0.28)' : '#f8fafc',
        backgroundColor: highlightThreePointRange ? 'rgba(248, 250, 252, 0.08)' : 'rgba(248, 250, 252, 0.14)',
        tension: 0.28,
        pointRadius: volumePoints.map((_, index) => (highlightThreePointRange && highlightedBuckets[index] ? 4 : 3)),
        pointBackgroundColor: volumePoints.map((_, index) =>
          highlightThreePointRange && !highlightedBuckets[index] ? 'rgba(248, 250, 252, 0.22)' : '#f8fafc'
        ),
        pointBorderColor: volumePoints.map((_, index) =>
          highlightThreePointRange && highlightedBuckets[index] ? '#fbbf24' : '#f8fafc'
        ),
        pointHoverRadius: 4,
        pointHitRadius: 6,
        borderWidth: 2.1,
        segment: {
          borderColor: (ctx) => {
            if (!highlightThreePointRange) return '#f8fafc';
            const nextBucket = data[ctx.p1DataIndex]?.distanceBucket ?? data[ctx.p0DataIndex]?.distanceBucket ?? 0;
            return inThreePointRange(nextBucket) ? '#f8fafc' : 'rgba(248, 250, 252, 0.22)';
          },
          borderWidth: (ctx) => {
            if (!highlightThreePointRange) return 2.1;
            const nextBucket = data[ctx.p1DataIndex]?.distanceBucket ?? data[ctx.p0DataIndex]?.distanceBucket ?? 0;
            return inThreePointRange(nextBucket) ? 3 : 1.5;
          }
        },
        yAxisID: 'volume'
      }
    ]
  } satisfies ChartData<'bar' | 'line'>;

  $: options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'nearest', intersect: true },
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
