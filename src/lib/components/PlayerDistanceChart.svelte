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

  import type { PlayerDistanceSeries, ShotOutcome } from '$lib/types';

  export let player: PlayerDistanceSeries | null = null;
  export let shotOutcome: ShotOutcome = 'all';
  export let revealProgress = 100;

  ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

  function withOpacity(hex: string, opacity: number) {
    const normalized = hex.replace('#', '');
    const bigint = Number.parseInt(normalized, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
  }

  function outcomeValue(
    row: PlayerDistanceSeries['seasons'][number] | undefined,
    selectedOutcome: ShotOutcome
  ): number | null {
    if (!row) return null;
    if (selectedOutcome === 'made') return row.avgMadeShotDistance;
    if (selectedOutcome === 'missed') return row.avgMissedShotDistance;
    return row.avgShotDistance;
  }

  function outcomeCount(
    row: PlayerDistanceSeries['seasons'][number] | undefined,
    selectedOutcome: ShotOutcome
  ): number {
    if (!row) return 0;
    if (selectedOutcome === 'made') return row.made;
    if (selectedOutcome === 'missed') return row.missed;
    return row.attempts;
  }

  function revealSeries(points: number[], progress: number) {
    const revealStartOffset = 25;
    const adjustedRevealProgress = Math.max(0, progress - revealStartOffset);
    const revealRatio = Math.max(0, Math.min(adjustedRevealProgress / (100 - revealStartOffset), 1));
    const revealIndexFloat = points.length > 1 ? revealRatio * (points.length - 1) : 0;
    const revealIndex = Math.floor(revealIndexFloat);
    const revealRemainder = revealIndexFloat - revealIndex;

    return points.map((value, index) => {
      if (index <= revealIndex) return value;
      if (index === revealIndex + 1 && revealRemainder > 0 && revealIndex >= 0 && revealIndex < points.length - 1) {
        const previous = points[revealIndex];
        return previous + (value - previous) * revealRemainder;
      }
      return null;
    });
  }

  function playerPoints(series: PlayerDistanceSeries | null, selectedOutcome: ShotOutcome) {
    if (!series) return [];
    return series.seasons.map((row) => outcomeValue(row, selectedOutcome) ?? 0);
  }

  $: datasetLabel =
    shotOutcome === 'made'
      ? 'Average Made Shot Distance'
      : shotOutcome === 'missed'
        ? 'Average Missed Shot Distance'
        : 'Average Shot Distance';
  $: activeColor =
    shotOutcome === 'made'
      ? { border: '#14b8a6', point: '#99f6e4', fill: 'rgba(20, 184, 166, 0.14)' }
      : shotOutcome === 'missed'
        ? { border: '#f97316', point: '#fdba74', fill: 'rgba(249, 115, 22, 0.14)' }
        : { border: '#fbbf24', point: '#fde68a', fill: 'rgba(251, 191, 36, 0.14)' };
  $: labels = player?.seasons.map((row) => row.season) ?? [];
  $: currentPoints = playerPoints(player, shotOutcome);
  $: revealedCurrentPoints = revealSeries(currentPoints, revealProgress);
  $: fullSeriesMin = currentPoints.length ? Math.min(...currentPoints) : 0;
  $: fullSeriesMax = currentPoints.length ? Math.max(...currentPoints) : 0;
  $: yPadding = Math.max(0.35, (fullSeriesMax - fullSeriesMin) * 0.18);
  $: fixedYMin = Math.max(0, +(fullSeriesMin - yPadding).toFixed(2));
  $: fixedYMax = +(fullSeriesMax + yPadding).toFixed(2);
  $: datasets = [
    ...(player
      ? [
          {
            label: player.player,
            data: revealedCurrentPoints,
            borderColor: activeColor.border,
            backgroundColor: activeColor.fill,
            pointBackgroundColor: activeColor.point,
            pointBorderColor: activeColor.border,
            pointBorderWidth: 1.4,
            pointRadius: revealedCurrentPoints.map((value) => (value === null ? 0 : 3)),
            pointHoverRadius: 5,
            spanGaps: false,
            tension: 0.28,
            fill: true,
            borderWidth: 2.5
          }
        ]
      : [])
  ];
  $: chartData = {
    labels,
    datasets
  } satisfies ChartData<'line'>;

  $: options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: { mode: 'nearest', intersect: false },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(2, 6, 23, 0.95)',
        borderColor: 'rgba(148, 163, 184, 0.18)',
        borderWidth: 1,
        callbacks: {
          label: (context) => {
            const row = player?.seasons[context.dataIndex];
            if (!row || context.raw == null) return `${context.dataset.label}: no attempts`;
            const countLabel =
              shotOutcome === 'made' ? 'Made shots' : shotOutcome === 'missed' ? 'Missed shots' : 'Attempts';
            return [
              `${context.dataset.label}: ${Number(context.raw).toFixed(2)} ft`,
              `${countLabel}: ${outcomeCount(row, shotOutcome).toLocaleString()}`
            ];
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

<div class="h-[30rem] lg:h-[38rem]">
  {#if player}
    <ChartCanvas type="line" data={chartData} {options} />
  {:else}
    <div class="flex h-full items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-400">
      No player distance trend data is available yet. Re-run the data pipeline to generate it.
    </div>
  {/if}
</div>
