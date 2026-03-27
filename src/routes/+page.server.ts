import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import type {
  DistancePayload,
  HeatmapPayload,
  MonthlyPayload,
  PlayerDistancePayload,
  SeasonDistancePayload
} from '$lib/types';
import type { PageServerLoad } from './$types';

const DATA_DIR = resolve('src/lib/data');

async function readJson<T>(filename: string): Promise<T | null> {
  try {
    const content = await readFile(resolve(DATA_DIR, filename), 'utf-8');
    return JSON.parse(content) as T;
  } catch {
    return null;
  }
}

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

export const load: PageServerLoad = async () => {
  const [heatmap, monthly, distance, seasonDistance, playerDistance] = await Promise.all([
    readJson<HeatmapPayload>('heatmap.json'),
    readJson<MonthlyPayload>('monthly-trends.json'),
    readJson<DistancePayload>('distance-profile.json'),
    readJson<SeasonDistancePayload>('season-distance-trend.json'),
    readJson<PlayerDistancePayload>('player-distance-trend.json')
  ]);

  const ready = Boolean(heatmap && monthly && distance);
  const resolvedSeasonDistance = seasonDistance ?? deriveSeasonDistancePayload(distance);

  return {
    pipelineReady: ready,
    heatmap,
    monthly,
    distance,
    seasonDistance: resolvedSeasonDistance,
    playerDistance,
    seasons: ready && heatmap ? heatmap.seasons : []
  };
};
