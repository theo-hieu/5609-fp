import type {
  DistancePayload,
  HeatmapPayload,
  MonthlyPayload,
  ShotTypeTrendPayload,
  PlayerDistancePayload,
  SeasonDistancePayload,
  ZoneTrendPayload
} from '$lib/types';
import type { PageLoad } from './$types';

function deriveSeasonDistancePayload(distance: DistancePayload | null): SeasonDistancePayload | null {
  if (!distance) return null;

  const bucketSize = distance.metadata.bucketSize;
  const longDistanceBucket = distance.metadata.longDistanceBucket;

  return {
    metadata: distance.metadata,
    seasons: distance.seasons,
    all: distance.seasons.map((season) => {
      const buckets = distance.bySeason[season] ?? [];
      const attempts = buckets.reduce((sum, bucket) => sum + bucket.attempts, 0);
      const made = buckets.reduce((sum, bucket) => sum + bucket.made, 0);
      const missed = buckets.reduce((sum, bucket) => sum + bucket.missed, 0);
      const weightedDistance = buckets.reduce((sum, bucket) => {
        const representativeDistance =
          bucket.distanceBucket >= longDistanceBucket
            ? longDistanceBucket
            : bucket.distanceBucket + bucketSize / 2;
        return sum + representativeDistance * bucket.attempts;
      }, 0);
      const weightedMadeDistance = buckets.reduce((sum, bucket) => {
        const representativeDistance =
          bucket.distanceBucket >= longDistanceBucket
            ? longDistanceBucket
            : bucket.distanceBucket + bucketSize / 2;
        return sum + representativeDistance * bucket.made;
      }, 0);
      const weightedMissedDistance = buckets.reduce((sum, bucket) => {
        const representativeDistance =
          bucket.distanceBucket >= longDistanceBucket
            ? longDistanceBucket
            : bucket.distanceBucket + bucketSize / 2;
        return sum + representativeDistance * bucket.missed;
      }, 0);

      return {
        season,
        attempts,
        made,
        missed,
        avgShotDistance: attempts ? +(weightedDistance / attempts).toFixed(2) : 0,
        avgMadeShotDistance: made ? +(weightedMadeDistance / made).toFixed(2) : 0,
        avgMissedShotDistance: missed ? +(weightedMissedDistance / missed).toFixed(2) : 0
      };
    })
  };
}

export const load: PageLoad = async () => {
  // Use Vite's dynamic imports to safely load the JSON files from $lib/data.
  // This works in the browser and during static prerendering, completely replacing node:fs.
  let heatmap = null, monthly = null, distance = null, seasonDistance = null, playerDistance = null,
    shotTypeTrend = null, zoneTrend = null;
  const optionalDataModules = import.meta.glob('../lib/data/*.json');

  try { heatmap = (await import('$lib/data/heatmap.json')).default as HeatmapPayload; } catch {}
  try { monthly = (await import('$lib/data/monthly-trends.json')).default as MonthlyPayload; } catch {}
  try { distance = (await import('$lib/data/distance-profile.json')).default as DistancePayload; } catch {}
  try { seasonDistance = (await import('$lib/data/season-distance-trend.json')).default as SeasonDistancePayload; } catch {}
  try { playerDistance = (await import('$lib/data/player-distance-trend.json')).default as PlayerDistancePayload; } catch {}
  try {
    const importer = optionalDataModules['../lib/data/shot-type-trend.json'];
    if (importer) shotTypeTrend = ((await importer()) as { default: ShotTypeTrendPayload }).default;
  } catch {}
  try {
    const importer = optionalDataModules['../lib/data/zone-trend.json'];
    if (importer) zoneTrend = ((await importer()) as { default: ZoneTrendPayload }).default;
  } catch {}

  const ready = Boolean(heatmap && monthly && distance);
  const resolvedSeasonDistance = seasonDistance ?? deriveSeasonDistancePayload(distance);

  return {
    pipelineReady: ready,
    heatmap,
    monthly,
    distance,
    seasonDistance: resolvedSeasonDistance,
    playerDistance,
    shotTypeTrend,
    zoneTrend,
    seasons: ready && heatmap ? heatmap.seasons : []
  };
};
