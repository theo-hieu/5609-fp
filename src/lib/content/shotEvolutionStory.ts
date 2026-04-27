import type {
  PlayerDistanceSeries,
  SeasonDistanceTrend,
  ShotTypeSeasonTrend,
  ZoneSeasonTrend
} from '$lib/types';

export type StoryMetric = {
  label: string;
  value: string;
  detail: string;
  tone: 'amber' | 'teal' | 'orange' | 'sky';
};

export type PlayerStoryCase = {
  player: string;
  label: string;
  title: string;
  body: string;
};

export const playerStoryCases: PlayerStoryCase[] = [
  {
    player: 'LeBron James',
    label: 'Longevity and adaptation',
    title: 'LeBron spans the whole rewrite.',
    body:
      'His career gives the story a long bridge: early-2000s rim pressure, the spacing boom, and late-career adaptation all sit on one timeline.'
  },
  {
    player: 'Stephen Curry',
    label: 'Stretches the ceiling',
    title: 'Curry makes distance feel normal.',
    body:
      'His profile turns deep attempts from novelty into structure, showing why the league could keep moving valuable shots farther out.'
  },
  {
    player: 'James Harden',
    label: 'Volume and math',
    title: 'Harden pressure-tests the shot-value equation.',
    body:
      'His career arc makes the tradeoff visible: fewer in-between possessions, more attempts that bend defenses toward the rim or the arc.'
  },
  {
    player: 'Kevin Durant',
    label: 'The exception',
    title: 'Durant keeps the middle alive.',
    body:
      'He is useful because he complicates the thesis: the league abandoned the middle, but elite shot-makers can still live there.'
  }
];

const percent = (value: number) => `${value.toFixed(1)}%`;
const feet = (value: number) => `${value.toFixed(2)} ft`;

function firstAndLast<T>(rows: T[]) {
  return {
    first: rows[0],
    last: rows[rows.length - 1]
  };
}

function shotTypeShare(row: ShotTypeSeasonTrend | undefined, shotType: string) {
  return 100 * (row?.shotTypes.find((entry) => entry.shotType === shotType)?.share ?? 0);
}

function zoneShare(row: ZoneSeasonTrend | undefined, zone: string) {
  return 100 * (row?.zones.find((entry) => entry.zone === zone)?.share ?? 0);
}

export function deriveThesisMetrics(
  seasonDistance: SeasonDistanceTrend[] = [],
  shotTypeTrend: ShotTypeSeasonTrend[] = [],
  zoneTrend: ZoneSeasonTrend[] = []
): StoryMetric[] {
  const distance = firstAndLast(seasonDistance);
  const shotTypes = firstAndLast(shotTypeTrend);
  const zones = firstAndLast(zoneTrend);

  if (!distance.first || !distance.last || !shotTypes.first || !shotTypes.last || !zones.first || !zones.last) {
    return [];
  }

  const firstSeason = distance.first.season;
  const lastSeason = distance.last.season;

  return [
    {
      label: 'Average shot distance',
      value: `${feet(distance.first.avgShotDistance)} -> ${feet(distance.last.avgShotDistance)}`,
      detail: `${firstSeason} to ${lastSeason}`,
      tone: 'amber'
    },
    {
      label: '3PT share',
      value: `${percent(shotTypeShare(shotTypes.first, '3PT Field Goal'))} -> ${percent(
        shotTypeShare(shotTypes.last, '3PT Field Goal')
      )}`,
      detail: 'The arc absorbs more possessions',
      tone: 'teal'
    },
    {
      label: 'Mid-range share',
      value: `${percent(zoneShare(zones.first, 'Mid-Range'))} -> ${percent(zoneShare(zones.last, 'Mid-Range'))}`,
      detail: 'The middle gets squeezed out',
      tone: 'orange'
    },
    {
      label: 'Above-break 3 share',
      value: `${percent(zoneShare(zones.first, 'Above the Break 3'))} -> ${percent(
        zoneShare(zones.last, 'Above the Break 3')
      )}`,
      detail: 'The biggest spatial expansion',
      tone: 'sky'
    }
  ];
}

export function playerDistanceSummary(player: PlayerDistanceSeries | null) {
  if (!player?.seasons.length) return 'No player trend data available.';

  const first = player.seasons[0];
  const last = player.seasons[player.seasons.length - 1];
  const peak = player.seasons.reduce((best, row) => (row.avgShotDistance > best.avgShotDistance ? row : best), first);

  return `${first.season}: ${feet(first.avgShotDistance)} -> ${last.season}: ${feet(
    last.avgShotDistance
  )}. Peak: ${feet(peak.avgShotDistance)} in ${peak.season}.`;
}
