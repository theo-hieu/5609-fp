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

  import type { ZoneSeasonTrend } from '$lib/types';

  export let data: ZoneSeasonTrend[] = [];
  export let zones: string[] = [];
  export let revealProgress = 100;

  const zoneColors: Record<string, string> = {
    'Restricted Area': '#fbbf24',
    'In The Paint (Non-RA)': '#fb7185',
    'Mid-Range': '#f97316',
    'Left Corner 3': '#38bdf8',
    'Right Corner 3': '#f472b6',
    'Above the Break 3': '#14b8a6',
    Backcourt: '#94a3b8'
  };

  ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

  function withOpacity(hex: string, opacity: number) {
    const normalized = hex.replace('#', '');
    const bigint = Number.parseInt(normalized, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
  }

  function zoneRow(season: ZoneSeasonTrend, zone: string) {
    return season.zones.find((entry) => entry.zone === zone);
  }

  $: labels = data.map((row) => row.season);
  $: revealStartOffset = 55;
  $: adjustedRevealProgress = Math.max(0, revealProgress - revealStartOffset);
  $: revealRatio = Math.max(0, Math.min(adjustedRevealProgress / (100 - revealStartOffset), 1));
  $: revealIndexFloat = labels.length > 1 ? revealRatio * (labels.length - 1) : 0;
  $: revealIndex = Math.floor(revealIndexFloat);
  $: revealRemainder = revealIndexFloat - revealIndex;
  $: emphasizeKeyZones = revealRatio >= 0.985;
  function revealSeries(points: number[]) {
    return points.map((value, index) => {
      if (index <= revealIndex) return value;
      if (index === revealIndex + 1 && revealRemainder > 0 && revealIndex >= 0 && revealIndex < points.length - 1) {
        const previous = points[revealIndex];
        return previous + (value - previous) * revealRemainder;
      }
      return null;
    });
  }
  $: allZoneSeries = zones.map((zone) => data.map((row) => +(100 * (zoneRow(row, zone)?.share ?? 0)).toFixed(1)));
  $: fullSeriesMax = allZoneSeries.flat().length ? Math.max(...allZoneSeries.flat()) : 0;
  $: fixedYMax = Math.max(5, Math.ceil((fullSeriesMax + 1.5) / 2) * 2);
  $: datasets = zones.map((zone) => {
    const baseColor = zoneColors[zone] ?? '#e2e8f0';
    const isKeyZone = zone === 'Above the Break 3' || zone === 'Mid-Range';
    const dimmedColor = withOpacity(baseColor, 0.22);

    return {
      label: zone,
      data: revealSeries(data.map((row) => +(100 * (zoneRow(row, zone)?.share ?? 0)).toFixed(1))),
      borderColor: emphasizeKeyZones && !isKeyZone ? dimmedColor : baseColor,
      backgroundColor: emphasizeKeyZones && !isKeyZone ? dimmedColor : baseColor,
      pointBackgroundColor: emphasizeKeyZones && !isKeyZone ? dimmedColor : baseColor,
      pointRadius: (ctx: { raw: unknown; dataIndex: number }) => {
        const value = ctx.raw;
        const index = ctx.dataIndex;
        return value == null || index > revealIndex + 1 ? 0 : 2.2;
      },
      pointHoverRadius: 4,
      tension: 0.25,
      borderWidth: emphasizeKeyZones ? (isKeyZone ? 4 : 1.6) : zone === 'Above the Break 3' || zone === 'Mid-Range' ? 3 : 2
    };
  });
  $: chartData = {
    labels,
    datasets
  } satisfies ChartData<'line'>;

  $: options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: { mode: 'nearest', intersect: false, axis: 'xy' },
    plugins: {
      legend: {
        position: 'bottom',
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
            const zone = context.dataset.label ?? '';
            const row = season ? zoneRow(season, zone) : null;
            if (!row) return `${zone}: no data`;
            return [
              `${zone}: ${Number(context.raw).toFixed(1)}%`,
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
        max: fixedYMax,
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

<div class="h-[26rem]">
  {#if data.length && zones.length}
    <Line data={chartData} {options} />
  {:else}
    <div class="flex h-full items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-400">
      No zone trend data is available yet. Re-run the data pipeline to generate it.
    </div>
  {/if}
</div>
