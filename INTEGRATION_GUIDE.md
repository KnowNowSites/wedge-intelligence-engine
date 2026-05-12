# WIE Integration Guide

This guide explains how to integrate the Python backend scrapers with the Express/React frontend.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                           │
│  (Dashboard, WedgeDetail, SignalExplorer, Watchlist)        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ tRPC API Calls
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Express Backend (Node.js)                       │
│  - tRPC Routers: wedges, signals, watchlist, scrapers       │
│  - Database: SQLite (local file)                            │
│  - Scheduler: APScheduler (Python subprocess)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Python Subprocess / HTTP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Python Backend (Background Services)             │
│  - 9 Scrapers (Reddit, HN, App Store, etc.)                │
│  - 7 Detectors (Pain Signal, Regulation, etc.)             │
│  - Scoring Engine & Profile Generator                       │
│  - APScheduler (runs on 24h-72h cadences)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Read/Write
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         SQLite Database (wie.db)                            │
│  - 11 Tables: signals, candidates, profiles, watchlist     │
└─────────────────────────────────────────────────────────────┘
```

## Integration Points

### 1. Frontend → Backend (tRPC)

**Dashboard Page** calls:
```typescript
trpc.wedges.list.useQuery({
  search: searchTerm,
  detector: filterDetector,
  complexity: filterComplexity,
  sortBy: sortBy,
})
```

**Wedge Detail Page** calls:
```typescript
trpc.wedges.get.useQuery({ id: wedgeId })
trpc.wedges.signals.useQuery({ wedgeId })
```

**Signal Explorer** calls:
```typescript
trpc.wedges.exploreSignals.useQuery({
  search: searchTerm,
  source: filterSource,
  type: filterType,
  sortBy: sortBy,
})
```

**Watchlist** calls:
```typescript
trpc.wedges.watchlist.useQuery()
trpc.wedges.addToWatchlist.useMutation()
trpc.wedges.updateWatchlistItem.useMutation()
trpc.wedges.removeFromWatchlist.useMutation()
trpc.wedges.exportWatchlist.useQuery()
```

### 2. Express Backend → Python Scrapers

**Option A: Subprocess Execution** (Recommended for local development)
```typescript
import { execSync } from 'child_process';

const result = execSync('python -m backend.scrapers.reddit_scraper', {
  cwd: '/home/ubuntu/wie',
  encoding: 'utf-8'
});
```

**Option B: HTTP API** (For separate Python server)
```typescript
const response = await fetch('http://localhost:8000/scrapers/reddit', {
  method: 'POST',
});
```

### 3. Python Backend → SQLite Database

All scrapers write to SQLite tables:
- `reddit_posts` - Reddit scraper results
- `hn_posts` - Hacker News results
- `app_store_reviews` - App Store reviews
- `play_store_reviews` - Play Store reviews
- `google_trends` - Google Trends data
- `producthunt_launches` - Product Hunt launches
- `sec_filings` - SEC EDGAR filings
- `job_postings` - Job posting data
- `yc_companies` - Y Combinator companies
- `openvc_companies` - OpenVC startup data
- `wedge_candidates` - Detector output
- `wedge_profiles` - Generated profiles
- `watchlist` - User watchlist

## Implementation Steps

### Step 1: Database Setup

The SQLite database is created automatically by `backend/database.py` on first run:

```bash
cd /home/ubuntu/wie
python -c "from backend.database import init_db; init_db()"
```

This creates `wie.db` in the project root with all 11 tables.

### Step 2: Configure Environment

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Fill in optional API credentials:
- `REDDIT_CLIENT_ID` - Reddit OAuth app ID
- `REDDIT_CLIENT_SECRET` - Reddit OAuth app secret
- `PRODUCTHUNT_API_TOKEN` - Product Hunt API token
- Other optional credentials

Scrapers will gracefully skip if credentials are missing.

### Step 3: Start the Application

**Local Development:**
```bash
cd /home/ubuntu/wie
make run
```

This starts:
1. Express server on port 3000
2. Scheduler in background
3. React dev server with HMR

**Docker:**
```bash
docker-compose up
```

### Step 4: Trigger Scrapers Manually

Use the tRPC endpoint to run a scraper:

```bash
curl -X POST http://localhost:3000/api/trpc/scrapers.run \
  -H "Content-Type: application/json" \
  -d '{"scraper": "reddit"}'
```

Or use the React UI (Signals page → Manual Trigger button).

### Step 5: Monitor Scheduler

The scheduler runs automatically and:
1. Executes each scraper on its cadence (24h-72h)
2. Runs all 7 detectors after each scraper
3. Generates profiles for wedges scoring > 15.0
4. Updates `scraper_metadata` table with timestamps

Check status via:
```bash
curl http://localhost:3000/api/trpc/scrapers.status
```

## Troubleshooting

### Scraper Fails Silently

1. Check logs: `tail -f .manus-logs/devserver.log`
2. Verify credentials in `.env`
3. Test scraper directly:
   ```bash
   python -m backend.scrapers.reddit_scraper
   ```

### Database Not Updating

1. Verify `wie.db` exists: `ls -la wie.db`
2. Check database permissions: `chmod 644 wie.db`
3. Inspect tables: `sqlite3 wie.db ".tables"`

### Scheduler Not Running

1. Check if APScheduler started: Look for `[Scheduler] Started` in logs
2. Verify no Python errors: `python -m backend.scheduler`
3. Check system resources: `free -h` (ensure enough memory)

### Frontend Shows No Data

1. Verify tRPC router is wired: Check `server/routers.ts`
2. Run a scraper manually to populate database
3. Check browser console for tRPC errors
4. Verify database has records: `sqlite3 wie.db "SELECT COUNT(*) FROM wedge_profiles;"`

## Next Steps

1. **Populate Database**: Run all 9 scrapers to collect initial data
2. **Test Detectors**: Verify each detector returns candidates
3. **Validate Scoring**: Check that wedges are ranked correctly
4. **Test Frontend**: Verify all filters and sorts work
5. **Deploy**: Use Manus UI to publish to production

## API Reference

### Scrapers Router

- `GET /api/trpc/scrapers.list` - List all available scrapers
- `POST /api/trpc/scrapers.run` - Manually trigger a scraper
- `GET /api/trpc/scrapers.status` - Get scraper status and metadata

### Wedges Router

- `GET /api/trpc/wedges.list` - List wedges with filters/sort
- `GET /api/trpc/wedges.get` - Get single wedge by ID
- `GET /api/trpc/wedges.signals` - Get signals for a wedge
- `GET /api/trpc/wedges.exploreSignals` - Get all signals with filters
- `GET /api/trpc/wedges.watchlist` - Get user's watchlist
- `POST /api/trpc/wedges.addToWatchlist` - Add wedge to watchlist
- `POST /api/trpc/wedges.updateWatchlistItem` - Update watchlist item
- `POST /api/trpc/wedges.removeFromWatchlist` - Remove from watchlist
- `GET /api/trpc/wedges.exportWatchlist` - Export watchlist as CSV

## Performance Considerations

1. **Scraper Timeouts**: Each scraper has a 30-second timeout
2. **Database Indexing**: Indexes on `wedge_score`, `detector_source`, `date_created`
3. **Pagination**: Frontend loads 20 wedges per page (implement lazy loading)
4. **Caching**: Consider Redis for frequently accessed wedges (future optimization)

## Security Notes

- All API credentials stored in `.env` (never committed)
- SQLite database file should be backed up regularly
- Consider adding authentication to scraper trigger endpoint (future)
- Watchlist data is currently public (add user isolation if needed)
