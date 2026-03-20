# NBA Shot Evolution

SvelteKit dashboard for NBA shot data aggregated from the season CSVs in `data_raw`. The app uses:

- `D3.js` for a half-court shot heatmap
- `Chart.js` via `svelte-chartjs` for monthly trend and distance charts
- `TailwindCSS` for the dashboard UI
- a standalone Python pipeline that reads local CSV files and writes compact JSON into `src/lib/data`

## Project Setup

Run these commands from `c:\Users\theoh\csci5609\nba-shot-evolution`.

### 1. Install frontend dependencies

```powershell
npm install
```

### 2. Prepare the raw CSV files

Place the season CSV files in `data_raw/`. This repo is already set up to read them directly.

If you want a helper script for the Kaggle source dataset, fill in `KAGGLE_USERNAME` and `KAGGLE_API_KEY` in `scripts/download_data.py`, then run:

```powershell
python scripts/download_data.py
```

### 3. Run the data pipeline

```powershell
python scripts/process_data.py
```

The script reads every `*.csv` file in `data_raw/` and rebuilds the aggregated JSON artifacts in `src/lib/data/`.

### 4. Start the dashboard

```powershell
npm run dev
```

### 5. Create a production build

```powershell
npm run build
```

## Data Pipeline Output

The pipeline writes lightweight aggregated files into `src/lib/data`:

- `heatmap.json`
- `monthly-trends.json`
- `distance-profile.json`

The frontend reads only these JSON files through SvelteKit server load. The raw CSVs never get shipped to the browser.

## Dashboard Features

- Half-court D3 heatmap using `LOC_X` and `LOC_Y`
- Interactive `Made` / `Missed` / `All Shots` filter
- Season dropdown filter
- Monthly shot volume line chart
- Monthly efficiency or miss-rate line chart
- Distance profile mixed chart with rate and shot volume

## File Guide

- `scripts/process_data.py`: local CSV aggregation pipeline
- `src/routes/+page.server.ts`: server-side loader for aggregated JSON
- `src/routes/+page.svelte`: main dashboard layout
- `src/lib/components/CourtHeatmap.svelte`: D3 shot heatmap with court overlay
- `src/lib/components/LineChart.svelte`: monthly line charts
- `src/lib/components/DistanceChart.svelte`: distance profile chart
- `src/lib/components/FilterBar.svelte`: interactive filters
