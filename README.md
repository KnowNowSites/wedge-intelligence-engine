# Wedge Intelligence Engine (WIE)

A full-stack market research tool that identifies profitable business wedges by scraping signals from 9+ sources, detecting strategic opportunities, scoring them, and surfacing results through an interactive React dashboard.

**Key Features:**
- **9 Independent Scrapers:** Reddit, Hacker News, App Store, Play Store, Google Trends, Product Hunt, SEC EDGAR, Job Postings, OpenVC
- **7 Wedge Detectors:** Pain signals, incumbent weakness, emerging categories, distribution gaps, regulation changes, margin expansion, geographic opportunities
- **Intelligent Scoring:** Multi-factor wedge score formula with expansion maps and evidence trails
- **Interactive Dashboard:** Filter, sort, search, and save wedges to a personal watchlist
- **Fully Local:** Zero paid APIs, runs entirely on your machine with SQLite
- **Single Command Startup:** `make run` or `docker-compose up`

---

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd wie
   ```

2. **Copy environment template and add credentials**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add:
   - **Reddit credentials** (get from https://www.reddit.com/prefs/apps)
   - **Product Hunt API token** (get from https://www.producthunt.com/v2/oauth/applications)

3. **Install dependencies**
   ```bash
   make install
   ```

4. **Initialize database**
   ```bash
   make init-db
   ```

5. **Start the application**
   ```bash
   make run
   ```

   The application will be available at:
   - **Frontend + API:** http://localhost:3000

---

## Architecture

### Directory Structure

```
wie/
├── backend/
│   ├── database.py             # SQLite schema and initialization
│   ├── config.py               # Configuration loader
│   ├── utils.py                # Shared utilities (logging, retries, delays)
│   ├── scoring.py              # Wedge scoring engine
│   ├── run_detectors.py        # Runs all 7 detectors in sequence
│   ├── run_scheduler.py        # Standalone scheduler entry point
│   ├── scrapers/
│   │   ├── reddit_scraper.py
│   │   ├── google_trends_scraper.py
│   │   ├── app_store_scraper.py
│   │   ├── play_store_scraper.py
│   │   ├── producthunt_scraper.py
│   │   ├── yc_scraper.py
│   │   ├── sec_edgar_scraper.py
│   │   ├── hackernews_scraper.py
│   │   ├── job_postings_scraper.py
│   │   ├── openvc_scraper.py
│   │   ├── amazon_reviews_scraper.py    # TODO: Stub (requires residential proxies)
│   │   └── g2_scraper.py                # TODO: Stub (requires premium solver infra)
│   ├── detectors/
│   │   ├── pain_signal.py
│   │   ├── incumbent_weakness.py
│   │   ├── emerging_category.py
│   │   ├── distribution_gap.py
│   │   ├── regulation_change.py
│   │   ├── margin_expansion.py
│   │   └── geographic_wedge.py
│   └── scheduler.py            # APScheduler configuration
├── server/                     # Express.js + tRPC backend
│   └── routers/
│       ├── wedges.ts           # Wedge profile queries (SQLite)
│       ├── scrapers.ts         # Scraper trigger endpoints
│       └── watchlist.ts        # Watchlist CRUD
├── client/                     # React frontend
│   └── src/
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── WedgeDetail.tsx
│       │   ├── Explorer.tsx
│       │   └── Watchlist.tsx
│       └── components/
├── wie.db                      # SQLite database (created on first run, git-ignored)
├── logs/
│   ├── scraper.log
│   └── scraper_errors.log
├── .env.example
├── .env                        # Your credentials (git-ignored)
├── requirements.txt
├── Makefile
├── docker-compose.yml
└── README.md
```

### Database Schema

**Key Tables:**
1. `signals` — Unified signal store for all scrapers (source, title, description, url, score)
2. `wedge_candidates` — Raw detector outputs with scoring dimensions
3. `wedge_profiles` — Final profiles for scores > 30.0
4. `watchlist` — User-saved wedges with notes and status
5. `scraper_metadata` — Last run times and error tracking

### Data Flow

```
Scrapers (9 modules)
    ↓
signals table (unified SQLite store)
    ↓
Detectors (7 modules, query signals table)
    ↓
wedge_candidates table
    ↓
Scoring Engine (normalized 0-100 scale)
    ↓
wedge_profiles (scores > 30.0)
    ↓
React Dashboard (filter, sort, search, save)
```

### Scraper Intervals

| Scraper | Interval | Reason |
|---------|----------|--------|
| Reddit | 24h | Daily discussions |
| Google Trends | 48h | Avoid rate limits |
| App Store | 48h | Daily reviews |
| Play Store | 48h | Daily reviews |
| Product Hunt | 24h | Daily launches |
| Y Combinator | 72h | Batch updates quarterly |
| SEC EDGAR | 72h | Quarterly filings |
| Hacker News | 24h | Daily discussions |
| Job Postings | 48h | Continuous hiring |
| OpenVC | 72h | Funding updates |

---

## Configuration

### Required Credentials

#### Reddit Scraper
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create another app" → "Script" → Fill in name and description
3. Copy: `client_id`, `client_secret`, your username, and password
4. Add to `.env`:
   ```
   REDDIT_USERNAME=your_username
   REDDIT_PASSWORD=your_password
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   ```

#### Product Hunt Scraper
1. Go to https://www.producthunt.com/v2/oauth/applications
2. Create a new application
3. Copy the API token
4. Add to `.env`:
   ```
   PRODUCTHUNT_API_TOKEN=your_token
   ```

### Optional Configuration

Edit `.env` to customize:
- **Scraper intervals** (in hours): `REDDIT_INTERVAL=24`, etc.
- **Wedge score threshold**: `WEDGE_SCORE_THRESHOLD=30.0`
- **Logging level**: `LOG_LEVEL=INFO`
- **Feature flags**: `SCHEDULER_ENABLED=true`, etc.

---

## Usage

### Start the Application

**Option 1: Direct (Recommended for development)**
```bash
make run
```

**Option 2: Docker**
```bash
make docker-up
```

**Option 3: Development with hot reload**
```bash
make dev
```

### Dashboard Views

#### 1. Main Dashboard (`/`)
- **Top wedges** ranked by score (0–100 scale)
- **Filter bar** by vertical, business model, capital, distribution, complexity
- **Sort options** by score, speed to $10k MRR, EV ceiling, capital, complexity
- **Global search** across all wedge profiles

#### 2. Wedge Detail (`/wedge/:id`)
- **Full profile** with all scoring dimensions
- **Expansion map** showing logical adjacencies (Step 1 → Step 2 → Step 3 → Step 4)
- **Evidence panel** with source quotes and links
- **Score breakdown** showing how each factor contributed
- **Save to watchlist** button

#### 3. Signal Explorer (`/explore`)
- **Raw signal feed** from all scrapers (newest first)
- **Filters** by source (Reddit, HN, App Store, etc.), date range, keyword, vertical
- **Links** to related wedges for each signal

#### 4. Watchlist (`/watchlist`)
- **Saved wedges** with personal notes (editable, persists to DB)
- **Status column** (Researching | Validating | Building | Rejected)
- **CSV export** button for all fields including evidence

---

## API Endpoints

### Wedges
- `GET /api/wedges` - List all wedge profiles
- `GET /api/wedges/:id` - Get single wedge detail
- `GET /api/wedges/search?q=...` - Search wedges
- `POST /api/wedges/filter` - Filter by criteria

### Signals
- `GET /api/signals` - List all raw signals
- `GET /api/signals/:source` - Filter by source

### Watchlist
- `GET /api/watchlist` - Get user's watchlist
- `POST /api/watchlist/:wedge_id` - Add to watchlist
- `DELETE /api/watchlist/:wedge_id` - Remove from watchlist
- `PATCH /api/watchlist/:wedge_id` - Update notes/status
- `GET /api/watchlist/export` - Export as CSV

### Scrapers (Admin)
- `GET /api/admin/scrapers/status` - Last run times and error counts
- `POST /api/admin/scrapers/:name/run` - Manually trigger a scraper
- `GET /api/admin/logs` - View scraper logs

---

## Scoring Formula

```
# All inputs normalized to 0–1 before multiplying
numerator   = pain × spend × growth × expandability × distribution
denominator = competition × capital × regulatory_friction
raw_score   = numerator / denominator

# Log-normalized to 0–100 scale
wedge_score = (log10(raw_score) + 5) × 10

If wedge_score > 30.0:
  - Auto-generate full profile
  - Apply 5 rejection filters
  - Store in wedge_profiles table
```

### Rejection Filters

A wedge is rejected if 2+ of these apply:
1. Parent market dominated by Google, Microsoft, Salesforce, or Amazon (no vertical escape route)
2. Capital required > $500k to reach first revenue
3. No distribution channel identified
4. 3+ funded startups already targeting identical entry segment
5. Regulatory barrier requires government license before first dollar

---

## Development

### Running Tests
```bash
make test
```

### Manually Running Scrapers
```bash
# Run a single scraper
python3 backend/scrapers/hackernews_scraper.py

# Run all detectors after scraping
python3 backend/run_detectors.py

# Check database state
python3 -c "
import sqlite3
c = sqlite3.connect('wie.db')
for t in ['signals', 'wedge_candidates', 'wedge_profiles']:
    print(t, c.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0])
"
```

### Adding a New Scraper

1. Create `backend/scrapers/my_scraper.py`
2. Save results to `signals` table with appropriate `source` tag
3. Use randomized delays (2–5 seconds) between requests
4. Add to `backend/scrapers/__init__.py`
5. Register in `scheduler.py`

### Adding a New Detector

1. Create `backend/detectors/my_detector.py`
2. Query the `signals` table filtered by relevant `source` values
3. Return list of wedge candidates with scoring dimensions
4. Add to `backend/detectors/__init__.py`
5. Register in `run_detectors.py`

---

## Troubleshooting

### Database Issues
```bash
# Reset database
rm wie.db
make init-db
```

### Scraper Failures
```bash
tail -f logs/scraper_errors.log
```

### Port Already in Use
```bash
# Kill existing process on port 3000
lsof -i :3000
```

### Missing Credentials
```bash
python3 -c "from backend.config import Config; Config.validate()"
```

---

## Hard Constraints

- ✅ Zero paid APIs required (all free tier or open source)
- ✅ No LinkedIn scraping (legal risk)
- ✅ No Crunchbase scraping (IP burn, no free API since 2025)
- ✅ Amazon Reviews and G2 are TODO stubs (require expensive infrastructure)
- ✅ All scrapers use 2–5 second randomized delays
- ✅ One scraper failure never crashes the pipeline
- ✅ App runs fully locally — no external cloud dependency

---

## Performance Notes

- **First run:** ~5–10 minutes to populate signals table (network dependent)
- **Detector runs:** ~30 seconds to process all signals
- **Scoring:** <1 second for all candidates
- **Dashboard load:** <500ms for filtered results

---

## Future Enhancements

- [ ] Claude API integration for narrative wedge synthesis
- [ ] Machine learning for pain signal classification
- [ ] Real-time signal streaming via WebSocket
- [ ] Competitor tracking and alerts
- [ ] Export to Notion/Airtable
- [ ] Multi-user support with authentication
- [ ] Advanced NLP for evidence extraction
- [ ] Market size estimation

---

## License

MIT

---

## Support

For issues or questions:
1. Check the logs: `logs/scraper_errors.log`
2. Review the configuration: `.env`
3. Validate credentials: `python3 -c "from backend.config import Config; Config.validate()"`
4. Open an issue on GitHub

---

**Built with:** Express.js, React, Tailwind CSS, SQLite, APScheduler, Playwright, BeautifulSoup4, pytrends
