<script lang="ts">
  import { Line } from 'svelte-chartjs';
  import {
    CategoryScale,
    Chart as ChartJS,
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

  ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

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
  $: datasets = player
    ? [
        {
          label: player.player,
          data: player.seasons.map((row) => outcomeValue(row, shotOutcome)),
          borderColor: activeColor.border,
          backgroundColor: activeColor.fill,
          pointBackgroundColor: activeColor.point,
          pointBorderColor: activeColor.border,
          pointBorderWidth: 1.4,
          pointRadius: 3,
          pointHoverRadius: 5,
          spanGaps: false,
          tension: 0.28,
          fill: true,
          borderWidth: 2.5
        }
      ]
    : [];
  $: chartData = {
    labels,
    datasets
  } satisfies ChartData<'line'>;

  $: options = {
    responsive: true,
    maintainAspectRatio: false,
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

<div class="h-[26rem]">
  {#if player}
    <Line data={chartData} {options} />
  {:else}
    <div class="flex h-full items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-400">
      No player distance trend data is available yet. Re-run the data pipeline to generate it.
    </div>
  {/if}
</div>
