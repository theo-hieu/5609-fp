import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

import type { DistancePayload, HeatmapPayload, MonthlyPayload } from '$lib/types';
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

export const load: PageServerLoad = async () => {
  const [heatmap, monthly, distance] = await Promise.all([
    readJson<HeatmapPayload>('heatmap.json'),
    readJson<MonthlyPayload>('monthly-trends.json'),
    readJson<DistancePayload>('distance-profile.json')
  ]);

  const ready = Boolean(heatmap && monthly && distance);

  return {
    pipelineReady: ready,
    heatmap,
    monthly,
    distance,
    seasons: ready && heatmap ? heatmap.seasons : []
  };
};
