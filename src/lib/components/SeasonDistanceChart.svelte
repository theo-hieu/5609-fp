<script lang="ts">
  import { Line } from 'svelte-chartjs';
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

  import type { SeasonDistanceTrend, ShotOutcome } from '$lib/types';

  export let data: SeasonDistanceTrend[] = [];
  export let shotOutcome: ShotOutcome = 'all';
  export let revealProgress = 100;

  ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

  $: labels = data.map((row) => row.season);
  $: points = data.map((row) =>
    shotOutcome === 'made'
      ? row.avgMadeShotDistance
      : shotOutcome === 'missed'
        ? row.avgMissedShotDistance
        : row.avgShotDistance
  );
  $: revealStartOffset = 25;
  $: adjustedRevealProgress = Math.max(0, revealProgress - revealStartOffset);
  $: revealRatio = Math.max(0, Math.min(adjustedRevealProgress / (100 - revealStartOffset), 1));
  $: revealIndexFloat = points.length > 1 ? revealRatio * (points.length - 1) : 0;
  $: revealIndex = Math.floor(revealIndexFloat);
  $: revealRemainder = revealIndexFloat - revealIndex;
  $: fullSeriesMin = points.length ? Math.min(...points) : 0;
  $: fullSeriesMax = points.length ? Math.max(...points) : 0;
  $: yPadding = Math.max(0.35, (fullSeriesMax - fullSeriesMin) * 0.18);
  $: fixedYMin = Math.max(0, +(fullSeriesMin - yPadding).toFixed(2));
  $: fixedYMax = +(fullSeriesMax + yPadding).toFixed(2);
  $: revealedPoints = points.map((value, index) => {
    if (index <= revealIndex) return value;
    if (index === revealIndex + 1 && revealRemainder > 0 && revealIndex >= 0 && revealIndex < points.length - 1) {
      const previous = points[revealIndex];
      return previous + (value - previous) * revealRemainder;
    }
    return null;
  });
  $: datasetLabel =
    shotOutcome === 'made'
      ? 'Average Made Shot Distance'
      : shotOutcome === 'missed'
        ? 'Average Missed Shot Distance'
        : 'Average Shot Distance';
  $: strokeColor = shotOutcome === 'made' ? '#14b8a6' : shotOutcome === 'missed' ? '#f97316' : '#fbbf24';
  $: fillColor =
    shotOutcome === 'made'
      ? 'rgba(20, 184, 166, 0.16)'
      : shotOutcome === 'missed'
        ? 'rgba(249, 115, 22, 0.16)'
        : 'rgba(251, 191, 36, 0.16)';
  $: pointBackgroundColor = shotOutcome === 'made' ? '#99f6e4' : shotOutcome === 'missed' ? '#fdba74' : '#fde68a';
  $: pointBorderColor = shotOutcome === 'made' ? '#0f766e' : shotOutcome === 'missed' ? '#c2410c' : '#f59e0b';
  $: chartData = {
    labels,
    datasets: [
      {
        label: datasetLabel,
        data: revealedPoints,
        borderColor: strokeColor,
        backgroundColor: fillColor,
        fill: true,
        tension: 0.28,
        pointRadius: revealedPoints.map((value, index) => (value === null || index > revealIndex + 1 ? 0 : 3)),
        pointHoverRadius: 5,
        pointBackgroundColor,
        pointBorderColor,
        pointBorderWidth: 1.5,
        borderWidth: 2.4
      }
    ]
  } satisfies ChartData<'line'>;

  $: options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
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
          label: (context) => `${context.dataset.label}: ${Number(context.raw).toFixed(2)} ft`,
          afterLabel: (context) => {
            const row = data[context.dataIndex];
            if (!row) return '';
            return shotOutcome === 'made'
              ? `Made shots: ${row.made.toLocaleString()}`
              : shotOutcome === 'missed'
                ? `Missed shots: ${row.missed.toLocaleString()}`
                : `Attempts: ${row.attempts.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#94a3b8',
          autoSkip: true,
          maxTicksLimit: 11
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.09)'
        }
      },
      y: {
        min: fixedYMin,
        max: fixedYMax,
        ticks: {
          color: '#cbd5e1',
          callback: (value) => `${value} ft`
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.09)'
        },
        title: {
          display: true,
          text: datasetLabel,
          color: '#e2e8f0'
        }
      }
    }
  } satisfies ChartOptions<'line'>;
</script>

<div class="h-[22rem]">
  {#if data.length}
    <Line data={chartData} {options} />
  {:else}
    <div class="flex h-full items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-400">
      No season distance trend data is available yet. Re-run the data pipeline to generate it.
    </div>
  {/if}
</div>
