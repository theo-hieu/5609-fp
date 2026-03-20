export type ShotOutcome = 'all' | 'made' | 'missed';

export interface FilterState {
  shotOutcome: ShotOutcome;
  season: string;
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
