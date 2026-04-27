<script lang="ts">
  import ChartCanvas from '$lib/components/ChartCanvas.svelte';
  import {
    BarElement,
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

  import type { DistanceBucket, ShotOutcome } from '$lib/types';

  export let data: DistanceBucket[] = [];
  export let shotOutcome: ShotOutcome = 'all';
  export let longDistanceBucket = 40;
  export let bucketSize = 2;
  export let highlightThreePointRange = false;
  export let merged = false;

  ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, Filler);

  function labelBucket(bucket: number) {
    if (bucket >= longDistanceBucket) return `${longDistanceBucket}+ ft`;
    return `${bucket}-${bucket + bucketSize} ft`;
  }

  function inThreePointRange(bucket: number) {
    return bucket >= 22;
  }

  function selectedAttempts(row: DistanceBucket) {
    if (shotOutcome === 'made') return row.made;
    if (shotOutcome === 'missed') return row.missed;
    return row.attempts;
  }

  function efficiencyValue(row: DistanceBucket) {
    if (!row.attempts) return 0;
    return shotOutcome === 'missed' ? (row.missed / row.attempts) * 100 : row.fgPct * 100;
  }

  function valueLabel(value: number) {
    return Number(value).toLocaleString();
  }

  function percentLabel(value: number) {
    return `${Number(value).toFixed(1)}%`;
  }

  $: totalSelectedAttempts = data.reduce((sum, row) => sum + selectedAttempts(row), 0);
  $: labels = data.map((row) => labelBucket(row.distanceBucket));
  $: highlightedBuckets = data.map((row) => inThreePointRange(row.distanceBucket));
  $: attemptValues = data.map((row) => selectedAttempts(row));
  $: efficiencyValues = data.map((row) => +efficiencyValue(row).toFixed(1));
  $: outcomeLabel = shotOutcome === 'all' ? 'all shots' : shotOutcome === 'made' ? 'made-shot lens' : 'missed-shot lens';
  $: attemptLabel = shotOutcome === 'all' ? 'Shot Attempts' : shotOutcome === 'made' ? 'Made Shots' : 'Missed Shots';
  $: efficiencyLabel = shotOutcome === 'missed' ? 'Miss Rate' : 'Field Goal Rate';
  $: attemptColor = shotOutcome === 'made' ? '#2dd4bf' : shotOutcome === 'missed' ? '#fb923c' : '#fbbf24';
  $: attemptFill = shotOutcome === 'made' ? 'rgba(45, 212, 191, 0.2)' : shotOutcome === 'missed' ? 'rgba(251, 146, 60, 0.2)' : 'rgba(251, 191, 36, 0.2)';
  $: efficiencyColor = shotOutcome === 'missed' ? '#fb923c' : '#14b8a6';
  $: efficiencyFill = shotOutcome === 'missed' ? 'rgba(249, 115, 22, 0.14)' : 'rgba(20, 184, 166, 0.14)';
  $: efficiencyBarColor = shotOutcome === 'missed' ? 'rgba(249, 115, 22, 0.82)' : 'rgba(20, 184, 166, 0.84)';
  $: dimmedEfficiencyBarColor = shotOutcome === 'missed' ? 'rgba(249, 115, 22, 0.18)' : 'rgba(20, 184, 166, 0.2)';
  $: highlightedEfficiencyBorderColor = shotOutcome === 'missed' ? 'rgba(253, 186, 116, 0.96)' : 'rgba(153, 246, 228, 0.96)';
  $: dimmedAttemptColor =
    shotOutcome === 'made' ? 'rgba(45, 212, 191, 0.28)' : shotOutcome === 'missed' ? 'rgba(251, 146, 60, 0.28)' : 'rgba(251, 191, 36, 0.28)';
  $: attemptPointColors = highlightedBuckets.map((highlighted) =>
    highlightThreePointRange && !highlighted ? dimmedAttemptColor : attemptColor
  );
  $: efficiencyBarColors = highlightedBuckets.map((highlighted) =>
    highlightThreePointRange && !highlighted ? dimmedEfficiencyBarColor : efficiencyBarColor
  );
  $: efficiencyBorderColors = highlightedBuckets.map((highlighted) =>
    highlightThreePointRange && highlighted ? highlightedEfficiencyBorderColor : 'rgba(15, 23, 42, 0)'
  );
  $: efficiencyBorderWidths = highlightedBuckets.map((highlighted) => (highlightThreePointRange && highlighted ? 1.4 : 0));

  $: efficiencyChartData = {
    labels,
    datasets: [
      {
        label: efficiencyLabel,
        data: efficiencyValues,
        backgroundColor: efficiencyBarColors,
        borderColor: efficiencyBorderColors,
        borderWidth: efficiencyBorderWidths,
        borderRadius: 7
      }
    ]
  } satisfies ChartData<'bar'>;

  $: attemptsChartData = {
    labels,
    datasets: [
      {
        label: attemptLabel,
        data: attemptValues,
        borderColor: attemptColor,
        backgroundColor: attemptFill,
        fill: true,
        tension: 0.32,
        pointRadius: attemptValues.length > 36 ? 0 : 3,
        pointHoverRadius: 5,
        pointBackgroundColor: attemptPointColors,
        pointBorderColor: attemptPointColors,
        segment: {
          borderColor: (context) => {
            if (!highlightThreePointRange) return attemptColor;
            const nextIndex = context.p1DataIndex ?? context.p0DataIndex ?? 0;
            return highlightedBuckets[nextIndex] ? attemptColor : dimmedAttemptColor;
          }
        },
        borderWidth: 2.4
      }
    ]
  } satisfies ChartData<'line'>;

  $: mergedChartData = {
    labels,
    datasets: [
      {
        type: 'bar' as const,
        label: efficiencyLabel,
        data: efficiencyValues,
        yAxisID: 'efficiency',
        backgroundColor: efficiencyBarColors,
        borderColor: efficiencyBorderColors,
        borderWidth: efficiencyBorderWidths,
        borderRadius: 7,
        order: 2
      },
      {
        type: 'line' as const,
        label: attemptLabel,
        data: attemptValues,
        yAxisID: 'attempts',
        borderColor: attemptColor,
        backgroundColor: attemptFill,
        fill: false,
        tension: 0.32,
        pointRadius: attemptValues.length > 36 ? 0 : 3.5,
        pointHoverRadius: 5,
        pointBackgroundColor: attemptPointColors,
        pointBorderColor: attemptPointColors,
        segment: {
          borderColor: (context) => {
            if (!highlightThreePointRange) return attemptColor;
            const nextIndex = context.p1DataIndex ?? context.p0DataIndex ?? 0;
            return highlightedBuckets[nextIndex] ? attemptColor : dimmedAttemptColor;
          }
        },
        borderWidth: 2.6,
        order: 1
      }
    ]
  } satisfies ChartData;

  $: baseInteractionOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 650,
      easing: 'easeOutQuart'
    },
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        display: false,
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
          title: (items) => items[0]?.label ?? '',
          label: (context) =>
            context.dataset.label === efficiencyLabel
              ? `${context.dataset.label}: ${percentLabel(Number(context.raw))}`
              : `${context.dataset.label}: ${valueLabel(Number(context.raw))}`,
          afterBody: (items) => {
            const index = items[0]?.dataIndex ?? -1;
            const row = data[index];
            if (!row) return [];
            const bucketTotal = selectedAttempts(row);
            const bucketShare = totalSelectedAttempts ? (bucketTotal / totalSelectedAttempts) * 100 : 0;
            return [
              `Bucket total: ${bucketTotal.toLocaleString()}`,
              `Bucket share: ${bucketShare.toFixed(2)}%`,
              `${efficiencyLabel}: ${percentLabel(efficiencyValues[index] ?? 0)}`
            ];
          }
        }
      }
    }
  } satisfies ChartOptions;

  $: efficiencyOptions = {
    ...baseInteractionOptions,
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
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          color: '#cbd5e1',
          callback: (value) => `${value}%`
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.08)'
        },
        title: {
          display: true,
          text: efficiencyLabel,
          color: '#e2e8f0'
        }
      }
    }
  } satisfies ChartOptions<'bar'>;

  $: attemptsOptions = {
    ...baseInteractionOptions,
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
      y: {
        beginAtZero: true,
        ticks: {
          color: '#cbd5e1',
          callback: (value) => Number(value).toLocaleString()
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.08)'
        },
        title: {
          display: true,
          text: attemptLabel,
          color: '#e2e8f0'
        }
      }
    }
  } satisfies ChartOptions<'line'>;

  $: mergedOptions = {
    ...baseInteractionOptions,
    plugins: {
      ...baseInteractionOptions.plugins,
      legend: {
        display: true,
        labels: {
          color: '#e2e8f0',
          usePointStyle: true,
          boxWidth: 10
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
      attempts: {
        type: 'linear' as const,
        position: 'left' as const,
        beginAtZero: true,
        ticks: {
          color: '#cbd5e1',
          callback: (value) => Number(value).toLocaleString()
        },
        grid: {
          color: 'rgba(148, 163, 184, 0.08)'
        },
        title: {
          display: true,
          text: attemptLabel,
          color: '#e2e8f0'
        }
      },
      efficiency: {
        type: 'linear' as const,
        position: 'right' as const,
        beginAtZero: true,
        max: 100,
        ticks: {
          color: '#cbd5e1',
          callback: (value) => `${value}%`
        },
        grid: {
          drawOnChartArea: false
        },
        title: {
          display: true,
          text: efficiencyLabel,
          color: '#e2e8f0'
        }
      }
    }
  } satisfies ChartOptions;
</script>

<div class="flex h-full min-h-[20rem] flex-col gap-4">
  {#if data.length}
    <div class="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Distance Distribution</p>
        <p class="mt-1 text-sm text-slate-300">
          Efficiency and selected shot attempts by distance, currently using the {outcomeLabel}. Hover a bucket for
          share of attempts and rate detail.
        </p>
      </div>
    </div>

    {#if merged}
      <div class="min-h-0 flex-1">
        <ChartCanvas type="bar" data={mergedChartData} options={mergedOptions} />
      </div>
    {:else}
      <div class="grid min-h-0 flex-1 gap-5 lg:grid-rows-2">
        <div class="min-h-[18rem]">
          <ChartCanvas type="bar" data={efficiencyChartData} options={efficiencyOptions} />
        </div>
        <div class="min-h-[18rem]">
          <ChartCanvas type="line" data={attemptsChartData} options={attemptsOptions} />
        </div>
      </div>
    {/if}
  {:else}
    <div class="flex h-full items-center justify-center rounded-2xl border border-dashed border-white/10 text-sm text-slate-400">
      No distance profile data is available for the current filter.
    </div>
  {/if}
</div>
