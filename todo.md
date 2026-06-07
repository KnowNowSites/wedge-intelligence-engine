# WIE Project TODO

## Phase 0: Project Structure & Database
- [x] Create backend directory structure with scrapers/, detectors/, and core modules
- [x] Create SQLite database schema with all 11 tables
- [x] Set up environment variables and .env file
- [x] Create Makefile and docker-compose.yml for single-command startup
- [x] Create README with setup instructions

## Phase 1: Data Scrapers (9 modules - FULL IMPLEMENTATION)
- [x] reddit_scraper.py - Playwright-based Reddit scraper with real logic
- [x] google_trends_scraper.py - pytrends-based trending keywords detector
- [x] app_store_scraper.py - Apple App Store reviews (1-2 star only)
- [x] play_store_scraper.py - Google Play Store reviews (1-2 star only)
- [x] producthunt_scraper.py - Product Hunt GraphQL API integration
- [x] yc_scraper.py - Y Combinator companies scraper
- [x] sec_edgar_scraper.py - SEC EDGAR filings keyword detector
- [x] hackernews_scraper.py - HN Algolia API integration
- [x] job_postings_scraper.py - Indeed RSS job postings scraper
- [x] openvc_scraper.py - OpenVC startup funding data
- [x] amazon_reviews_scraper.py - TODO stub (residential proxy cost)
- [x] g2_scraper.py - TODO stub (bot protection too aggressive)
- [ ] Integrate scrapers into Express backend as background services
- [ ] Add POST /api/scrapers/run/:scraper_name endpoint for manual testing
- [ ] Implement graceful degradation for missing credentials

## Phase 2: Wedge Detectors & Scoring
- [x] pain_signal.py - Detect high-volume complaints and negative sentiment
- [x] incumbent_weakness.py - Group complaints by company/software
- [x] emerging_category.py - Find fragmented markets with multiple players
- [x] distribution_gap.py - Find rising keywords with no clear SaaS leader
- [x] regulation_change.py - Cluster regulatory mentions across sources
- [x] margin_expansion.py - Identify high-margin manual service opportunities
- [x] geographic_wedge.py - Find geographic arbitrage opportunities
- [x] scoring.py - Implement wedge_score formula and helper functions
- [x] wedge_profile_generator.py - Auto-generate profiles for scores > 15.0

## Phase 3: Scheduler & Background Jobs
- [x] scheduler.py - APScheduler setup with 24h-72h cadences per scraper
- [x] Background task runner - Re-run detectors after each scraper
- [x] Last-refreshed timestamp tracking

## Phase 4: React Frontend Dashboard
- [x] Dashboard page (/) - Ranked wedge cards with filters and sort
- [x] Wedge Detail page (/wedge/:id) - Full profile, expansion map, evidence
- [x] Signal Explorer page (/signals) - Raw signal feed with filters
- [x] Watchlist page (/watchlist) - Notes field, status column, CSV export
- [x] Navigation header with routing
- [x] tRPC routers for wedges, signals, watchlist

## Phase 5: Integration & Testing
- [x] All scrapers run independently without crashing each other (error handling in place)
- [x] Database schema created with all 11 tables
- [x] All 7 detectors implemented with query logic
- [x] Scoring formula correctly ranks candidates
- [x] Dashboard loads and displays wedges with working filters
- [x] Wedge detail page renders full profile + expansion map
- [x] Signal Explorer shows raw records with source attribution
- [x] Watchlist CRUD operations functional (tRPC procedures)
- [x] Scheduler configured with APScheduler (24h-72h cadences)
- [x] Single startup command ready: make run or docker-compose up
- [x] All 32 wedges router tests passing

## Phase 6: Documentation & Delivery
- [x] Complete README with architecture overview (README_COMPLETE.md)
- [x] Setup instructions for API credentials
- [x] Example .env file (.env.example)
- [x] Architecture diagram (ARCHITECTURE.md)
- [x] Integration guide (INTEGRATION_GUIDE.md)
- [x] Backend module documentation (backend/README.md)
- [x] Frontend component documentation (client/README.md)
- [x] Dashboard page integrated with real tRPC data
- [x] WedgeDetail page integrated with real tRPC data
- [x] SignalExplorer page integrated with real tRPC data
- [x] Watchlist page integrated with real tRPC data
- [x] All 32 wedges router tests passing
- [x] Final testing and bug fixes
- [ ] Publish to production


## Surgical Fix: Unify Database on SQLite (COMPLETED)
- [x] Step 1: Remove MySQL/Drizzle imports and fix TypeScript errors
- [x] Step 2: Delete create_repo.py and update .gitignore
- [x] Step 3: Install better-sqlite3 (pragmatic pivot to Python API proxy)
- [x] Step 4: Rewrite wedges router with real SQLite queries (via Python API)
- [x] Step 5: Verify tRPC endpoints return real data from database
- [x] Step 6: Verify all 12 wedges load correctly on Dashboard
- [x] Step 7: Verify signals load correctly on Signal Explorer
- [x] Step 8: Verify watchlist CRUD operations work

## Architecture Decision
- **Final Approach**: Python HTTP API proxy for database access
- **Rationale**: Simpler than native module compilation, maintains single source of truth
- **Status**: All systems operational, 12 wedges loaded, tRPC working
