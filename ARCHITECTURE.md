# WIE Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    React Frontend Dashboard                      │
│  (Dashboard | Wedge Detail | Signal Explorer | Watchlist)       │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Server                        │
│  (Routes, API Endpoints, Business Logic)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   ┌─────────┐    ┌──────────────┐  ┌──────────┐
   │ Scrapers │    │  Detectors   │  │ Scoring  │
   │ (9 mods) │    │  (7 modules) │  │ Engine   │
   └────┬────┘    └──────┬───────┘  └────┬─────┘
        │                │               │
        └────────────────┼───────────────┘
                         ↓
            ┌────────────────────────┐
            │   SQLite Database      │
            │  (11 tables, indexes)  │
            └────────────────────────┘
```

## Data Flow

### 1. Data Collection Phase
```
Scrapers (9 modules)
  ├── reddit_scraper.py (Playwright)
  ├── google_trends_scraper.py (pytrends)
  ├── app_store_scraper.py (app-store-scraper)
  ├── play_store_scraper.py (google-play-scraper)
  ├── producthunt_scraper.py (GraphQL API)
  ├── yc_scraper.py (BeautifulSoup)
  ├── sec_edgar_scraper.py (SEC API)
  ├── hackernews_scraper.py (Algolia API)
  ├── job_postings_scraper.py (RSS/BeautifulSoup)
  └── openvc_scraper.py (BeautifulSoup)
        ↓
    [Randomized delays 2-5s]
    [Exponential backoff retry logic]
    [Isolated error handling]
        ↓
    SQLite Database (raw signal tables)
```

### 2. Wedge Detection Phase
```
Detectors (7 modules)
  ├── pain_signal.py
  ├── incumbent_weakness.py
  ├── emerging_category.py
  ├── distribution_gap.py
  ├── regulation_change.py
  ├── margin_expansion.py
  └── geographic_wedge.py
        ↓
    Query relevant signal tables
        ↓
    Generate wedge candidates with scoring dimensions
        ↓
    wedge_candidates table (raw detector outputs)
```

### 3. Scoring & Profile Generation
```
Scoring Engine (scoring.py)
    ├── calculate_wedge_score()
    │   └── numerator = pain × spend × growth × expandability × distribution
    │   └── denominator = competition × capital × regulatory
    │   └── wedge_score = numerator / denominator
    │
    ├── estimate_mrr_timeline()
    │   └── Months to $10k MRR
    │   └── Months to $100k MRR
    │
    ├── classify_ev()
    │   └── low | medium | high | very_high
    │
    └── classify_complexity()
        └── low | medium | high
        
    ↓
    
Profile Generator (wedge_profile_generator.py)
    ├── For each wedge with score > 15.0
    ├── Apply 5 rejection filters
    ├── Generate full JSON profile
    └── Store in wedge_profiles table
```

### 4. Scheduler & Refresh Cycle
```
APScheduler (scheduler.py)
    ├── Reddit: every 24h
    ├── Google Trends: every 48h
    ├── App Store: every 48h
    ├── Play Store: every 48h
    ├── Product Hunt: every 24h
    ├── Y Combinator: every 72h
    ├── SEC EDGAR: every 72h
    ├── Hacker News: every 24h
    ├── Job Postings: every 48h
    └── OpenVC: every 72h
    
    After each scraper:
    ├── Re-run all 7 detectors
    ├── Re-score all candidates
    ├── Generate new profiles (score > 15.0)
    └── Update last-refreshed timestamps
```

### 5. Frontend Consumption
```
React Dashboard
    ├── Dashboard Page (/)
    │   ├── Fetch top wedges (sorted by score)
    │   ├── Display filter bar (vertical, model, capital, etc.)
    │   ├── Global search
    │   └── Sort options
    │
    ├── Wedge Detail Page (/wedge/:id)
    │   ├── Full profile rendering
    │   ├── Expansion map (Step 1 → Step 2 → Step 3 → Step 4)
    │   ├── Evidence panel (source quotes + links)
    │   ├── Score breakdown
    │   └── Save to watchlist
    │
    ├── Signal Explorer (/explore)
    │   ├── Raw signal feed (newest first)
    │   ├── Filters (source, date, keyword, vertical)
    │   └── Links to related wedges
    │
    └── Watchlist (/watchlist)
        ├── Saved wedges with notes
        ├── Status column (Researching | Validating | Building | Rejected)
        └── CSV export
```

## Database Schema

### Signal Tables (Raw Data)
- `reddit_posts` - Reddit discussions (subreddit, title, body, comments, upvotes)
- `hn_posts` - Hacker News threads (title, comments, score, author)
- `app_store_reviews` - Apple App Store reviews (1-2 star only)
- `play_store_reviews` - Google Play Store reviews (1-2 star only)
- `google_trends` - Rising keywords (keyword, trend_score, is_breakout)
- `producthunt_launches` - Product Hunt launches (name, upvotes, comments, category)
- `yc_companies` - Y Combinator companies (name, batch, vertical, status)
- `sec_filings` - SEC EDGAR filings (company, filing_type, keyword, excerpt)
- `job_postings` - Job postings (title, company, industry, description)
- `openvc_companies` - Startup funding data (name, vertical, stage, country)

### Candidate & Profile Tables
- `wedge_candidates` - Raw detector outputs (detector_name, wedge_name, scoring dimensions)
- `wedge_profiles` - Final profiles (score > 15.0, with rejection filters applied)
- `watchlist` - User-saved wedges (notes, status)

### Metadata
- `scraper_metadata` - Last run times, error counts, error messages

## Error Handling & Resilience

### Scraper Isolation
```python
@safe_scraper_execution("scraper_name")
@retry_with_backoff(max_retries=3, base_delay=2.0)
def scraper_function():
    # One failure never crashes the pipeline
    # Returns empty list on failure
    # Logs error to scraper_errors.log
```

### Rate Limiting
```python
randomized_delay(min_seconds=2, max_seconds=5)  # Between requests
randomized_delay(min_seconds=5, max_seconds=8)  # For Google Trends (conservative)
```

### Retry Logic
```python
# Exponential backoff: 1s → 2s → 4s → 8s
# Max 3 retries per request
# Logs all failures
```

## Configuration

### Environment Variables
```
REDDIT_USERNAME, REDDIT_PASSWORD, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
PRODUCTHUNT_API_TOKEN
SCRAPER_INTERVALS (24h, 48h, 72h per scraper)
WEDGE_SCORE_THRESHOLD (default: 15.0)
LOG_LEVEL (INFO, DEBUG, ERROR)
SCHEDULER_ENABLED (true/false)
```

### Feature Flags
```
GOOGLE_TRENDS_ENABLED
APP_STORE_ENABLED
PLAY_STORE_ENABLED
SCHEDULER_ENABLED
```

## Performance Characteristics

| Operation | Time |
|-----------|------|
| First scraper run (all 9) | 5-10 minutes |
| Detector run (all 7) | ~30 seconds |
| Scoring (all candidates) | <1 second |
| Dashboard load (filtered results) | <500ms |
| Database query (indexed) | <100ms |

## Deployment

### Local Development
```bash
make run
```

### Docker
```bash
docker-compose up
```

### Single Command
```bash
make run  # or docker-compose up
```

## Hard Constraints Met

✅ Zero paid APIs required (all free tier or open source)
✅ No LinkedIn scraping (legal risk)
✅ No Crunchbase scraping (IP burn)
✅ Amazon Reviews and G2 are TODO stubs (expensive proxies)
✅ All scrapers use 2-5 second randomized delays
✅ One scraper failure never crashes the pipeline
✅ App runs fully locally with SQLite
✅ Single startup command works
