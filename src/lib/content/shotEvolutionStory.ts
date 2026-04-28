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
  },
  {
    player: 'Nikola Jokic',
    label: 'Modern center skill',
    title: 'Jokic stretches the center archetype.',
    body:
      'His profile shows how modern bigs can bend defenses without looking like traditional perimeter guards, mixing touch, range, and playmaking gravity.'
  },
  {
    player: 'Luka Doncic',
    label: 'Young heliocentric creator',
    title: 'Luka enters with the modern map already built.',
    body:
      'His career starts after the three-point boom is normal, making him useful for seeing how newer stars inherit deep pull-ups and spread spacing as a baseline.'
  },
  {
    player: 'Anthony Edwards',
    label: 'Next-wave pressure',
    title: 'Edwards represents the newer scoring wing.',
    body:
      'His early career sits in the fully modern shot economy, where downhill rim pressure and confident perimeter attempts are expected from young stars.'
  },
  {
    player: 'Kobe Bryant',
    label: 'Pre-boom shot-maker',
    title: 'Kobe anchors the midrange era.',
    body:
      'His profile gives the project an older star comparison: high-volume shot creation before the league fully reorganized around threes and rim attempts.'
  },
  {
    player: 'Tim Duncan',
    label: 'Interior foundation',
    title: 'Duncan shows the old big-man baseline.',
    body:
      'His career is a strong contrast case because his value was rooted near the basket and in the post, not in expanding farther behind the arc.'
  },
  {
    player: 'Giannis Antetokounmpo',
    label: 'Rim pressure in the modern era',
    title: 'Giannis keeps the paint central.',
    body:
      'He shows that the modern revolution did not eliminate interior dominance; it made spacing around elite rim pressure even more important.'
  },
  {
    player: "Shaquille O'Neal",
    label: 'Pure interior force',
    title: 'Shaq is the clearest no-three contrast.',
    body:
      'His profile is a useful extreme: almost everything is built around power near the rim, making the modern spacing shift easier to compare against.'
  },
  {
    player: 'Jayson Tatum',
    label: 'Modern wing volume',
    title: 'Tatum reflects the contemporary star wing.',
    body:
      'His shot profile belongs to the era where large wings are expected to create from three, attack mismatches, and scale their range with volume.'
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
