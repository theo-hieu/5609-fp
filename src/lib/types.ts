export type ShotOutcome = 'all' | 'made' | 'missed';
export type SceneId = 1 | 2 | 3;

export interface FilterState {
  shotOutcome: ShotOutcome;
  season: string;
}

export interface SceneCopy {
  id: SceneId;
  eyebrow: string;
  title: string;
  description: string;
  paragraphs: string[];
}

export interface AggregateStats {
  attempts: number;
  made: number;
  missed: number;
  fgPct: number;
}

export interface HeatmapCell extends AggregateStats {
  x: number;
  y: number;
}

export interface MonthlyTrend extends AggregateStats {
  month: string;
}

export interface DistanceBucket extends AggregateStats {
  distanceBucket: number;
}

export interface SeasonDistanceTrend {
  season: string;
  attempts: number;
  made: number;
  missed: number;
  avgShotDistance: number;
  avgMadeShotDistance: number;
  avgMissedShotDistance: number;
}

export interface PlayerSeasonDistanceTrend extends SeasonDistanceTrend {}

export interface PlayerDistanceSeries {
  player: string;
  firstSeason: string | null;
  seasons: PlayerSeasonDistanceTrend[];
}

export interface DataCollection<T> {
  seasons: string[];
  all: T[];
  bySeason: Record<string, T[]>;
}

export interface DataMetadata {
  dataset: string;
  generatedAt: string;
  recordCount: number;
  skippedRows: number;
}

export interface HeatmapMetadata extends DataMetadata {
  cellSize: number;
  fullCourtLength: number;
  halfCourtLength: number;
  halfCourtWidth: number;
}

export interface DistanceMetadata extends DataMetadata {
  bucketSize: number;
  longDistanceBucket: number;
}

export interface HeatmapPayload extends DataCollection<HeatmapCell> {
  metadata: HeatmapMetadata;
}

export interface MonthlyPayload extends DataCollection<MonthlyTrend> {
  metadata: DataMetadata;
}

export interface DistancePayload extends DataCollection<DistanceBucket> {
  metadata: DistanceMetadata;
}

export interface SeasonDistancePayload {
  metadata: DataMetadata;
  seasons: string[];
  all: SeasonDistanceTrend[];
}

export interface PlayerDistancePayload {
  metadata: DataMetadata;
  seasons: string[];
  players: PlayerDistanceSeries[];
}
