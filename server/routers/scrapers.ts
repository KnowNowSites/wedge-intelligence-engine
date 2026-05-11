import { z } from "zod";
import { publicProcedure, router } from "../_core/trpc";

const VALID_SCRAPERS = [
  "reddit",
  "google_trends",
  "app_store",
  "play_store",
  "producthunt",
  "yc",
  "sec_edgar",
  "hackernews",
  "job_postings",
  "openvc",
] as const;

type ScraperName = (typeof VALID_SCRAPERS)[number];

const SCRAPER_DESCRIPTIONS: Record<ScraperName, string> = {
  reddit: "Extracts pain signals from targeted subreddits",
  google_trends: "Detects rising keywords in B2B/vertical SaaS categories",
  app_store: "Scrapes 1-2 star App Store reviews with unmet needs",
  play_store: "Scrapes 1-2 star Play Store reviews with unmet needs",
  producthunt: "Fetches new product launches from last 90 days",
  yc: "Extracts Y Combinator companies by batch and vertical",
  sec_edgar: "Finds regulatory and market signals in SEC filings",
  hackernews: "Extracts problem statements from Hacker News",
  job_postings: "Detects manual job titles indicating scaling gaps",
  openvc: "Gathers startup funding data (free Crunchbase alternative)",
};

export const scrapersRouter = router({
  /**
   * List all available scrapers
   */
  list: publicProcedure.query(async () => {
    return {
      scrapers: VALID_SCRAPERS.map((name) => ({
        name,
        description: SCRAPER_DESCRIPTIONS[name],
      })),
    };
  }),

  /**
   * Manually trigger a single scraper
   * POST /api/trpc/scrapers.run
   *
   * This endpoint calls the Python backend scraper via subprocess
   * or HTTP if running separately.
   */
  run: publicProcedure
    .input(
      z.object({
        scraper: z.enum(VALID_SCRAPERS),
      })
    )
    .mutation(async ({ input }) => {
      const { scraper } = input;

      try {
        console.log(`[Scrapers] Manually triggering: ${scraper}`);

        // TODO: Implement scraper execution
        // Option 1: Call Python backend via HTTP
        // const response = await fetch(`http://localhost:8000/scrapers/${scraper}`, {
        //   method: 'POST',
        // });

        // Option 2: Use child_process to run Python directly
        // const { execSync } = require('child_process');
        // const result = execSync(`python -m backend.scrapers.${scraper}_scraper`);

        // For now, return a placeholder response
        return {
          success: true,
          scraper,
          results_fetched: 0,
          results_saved: 0,
          message: "Scraper execution not yet integrated",
          timestamp: new Date().toISOString(),
        };
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : String(error);
        console.error(`[Scrapers] Error running ${scraper}:`, errorMessage);

        return {
          success: false,
          scraper,
          error: errorMessage,
          timestamp: new Date().toISOString(),
        };
      }
    }),

  /**
   * Get status of all scrapers (last run time, error count, etc.)
   */
  status: publicProcedure.query(async () => {
    // TODO: Query scraper_metadata table from database
    return {
      scrapers: VALID_SCRAPERS.map((name) => ({
        name,
        last_run: null,
        last_successful_run: null,
        error_count: 0,
        last_error: null,
      })),
    };
  }),
});
