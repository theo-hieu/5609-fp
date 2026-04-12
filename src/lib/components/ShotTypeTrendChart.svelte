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

  import type { ShotTypeSeasonTrend } from '$lib/types';

  export let data: ShotTypeSeasonTrend[] = [];
  export let revealProgress = 100;

  ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

  function shotTypeRow(season: ShotTypeSeasonTrend, shotType: string) {
    return season.shotTypes.find((entry) => entry.shotType === shotType);
  }

  $: labels = data.map((row) => row.season);
  $: revealStartOffset = 40;
  $: adjustedRevealProgress = Math.max(0, revealProgress - revealStartOffset);
  $: effectiveRevealProgress = Math.max(0, Math.min((adjustedRevealProgress / (100 - revealStartOffset)) * 100, 100));
  $: revealPlugin = {
    id: 'datasetReveal',
    beforeDatasetsDraw(chart: ChartJS) {
      const { ctx, chartArea } = chart;
      if (!chartArea) return;

      const reveal = effectiveRevealProgress / 100;
      const width = (chartArea.right - chartArea.left) * reveal;

      ctx.save();
      ctx.beginPath();
      ctx.rect(chartArea.left, chartArea.top, width, chartArea.bottom - chartArea.top);
      ctx.clip();
    },
    afterDatasetsDraw(chart: ChartJS) {
      chart.ctx.restore();
    }
  };
  $: chartData = {
    labels,
    datasets: [
      {
        label: '2PT Share',
        data: data.map((row) => +(100 * (shotTypeRow(row, '2PT Field Goal')?.share ?? 0)).toFixed(1)),
        borderColor: '#f97316',
        backgroundColor: '#f97316',
        pointBackgroundColor: '#fdba74',
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.25,
        borderWidth: 2.6
      },
      {
        label: '3PT Share',
        data: data.map((row) => +(100 * (shotTypeRow(row, '3PT Field Goal')?.share ?? 0)).toFixed(1)),
        borderColor: '#14b8a6',
        backgroundColor: '#14b8a6',
        pointBackgroundColor: '#99f6e4',
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.25,
        borderWidth: 2.6
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
        labels: {
          color: '#e2e8f0',
          usePointStyle: true,
          boxWidth: 10
        }
      },
      tooltip: {
        backgroundColor: 'rgba(2, 6, 23, 0.95)',
        borderColor: 'rgba(148, 163, 184, 0.18)',
        borderWidth: 1,
        callbacks: {
          label: (context) => {
            const season = data[context.dataIndex];
            const shotType = context.datasetIndex === 0 ? '2PT Field Goal' : '3PT Field Goal';
            const row = season ? shotTypeRow(season, shotType) : null;
            if (!row) return `${context.dataset.label}: no data`;
            return [
              `${context.dataset.label}: ${Number(context.raw).toFixed(1)}%`,
              `Attempts: ${row.attempts.toLocaleString()}`
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
        min: 0,
        max: 100,
        ticks: {
          color: '#cbd5e1',
          callback: (value) => `${value}%`
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.09)'
        },
        title: {
          display: true,
          text: 'Share of Shot Attempts',
          color: '#e2e8f0'
        }
      }
    }
  } satisfies ChartOptions<'line'>;
</script>

<div class="h-[22rem]">
  {#if data.length}
    <Line data={chartData} {options} plugins={[revealPlugin as never]} />
  {:else}
    <div class="flex h-full items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-400">
      No shot type trend data is available yet. Re-run the data pipeline to generate it.
    </div>
  {/if}
</div>
