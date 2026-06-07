import { z } from "zod";
import { publicProcedure, router } from "../_core/trpc";
import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";
import * as db from "../db";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BACKEND_PATH = path.join(__dirname, "..", "..", "backend");

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

/**
 * Execute a Python scraper as a subprocess
 */
function executeScraper(scraperName: ScraperName): Promise<{
  success: boolean;
  results_fetched: number;
  results_saved: number;
  error?: string;
}> {
  return new Promise((resolve) => {
    const startTime = Date.now();
    let output = "";
    let errorOutput = "";

    const pythonProcess = spawn("python3", [
      "-m",
      `backend.scrapers.${scraperName}_scraper`,
      "--db",
      path.join(__dirname, "..", "..", "wie.db"),
    ]);

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
      console.log(`[${scraperName}] ${data}`);
    });

    pythonProcess.stderr.on("data", (data) => {
      errorOutput += data.toString();
      console.error(`[${scraperName}] ERROR: ${data}`);
    });

    pythonProcess.on("close", (code) => {
      const duration = Date.now() - startTime;
      console.log(
        `[${scraperName}] Process exited with code ${code} (${duration}ms)`
      );

      // Update metadata
      try {
        if (code === 0) {
          db.updateScraperMetadata(scraperName, {
            last_run: new Date(),
            last_successful_run: new Date(),
            error_count: 0,
            last_error: null,
            results_count: 0, // Will be updated by scraper
          });

          resolve({
            success: true,
            results_fetched: 0,
            results_saved: 0,
          });
        } else {
          // Get metadata - note: db functions are async but we can't await in event handler
          // Use a default value for now
          const metadata: any = null; // Metadata will be 0 for error_count
          db.updateScraperMetadata(scraperName, {
            last_run: new Date(),
            error_count: (metadata?.error_count || 0) + 1,
            last_error: errorOutput || `Process exited with code ${code}`,
          });

          resolve({
            success: false,
            results_fetched: 0,
            results_saved: 0,
            error: errorOutput || `Process exited with code ${code}`,
          });
        }
      } catch (err) {
        console.error(`[${scraperName}] Failed to update metadata:`, err);
        resolve({
          success: false,
          results_fetched: 0,
          results_saved: 0,
          error: String(err),
        });
      }
    });

    pythonProcess.on("error", (err) => {
      console.error(`[${scraperName}] Failed to start process:`, err);
      resolve({
        success: false,
        results_fetched: 0,
        results_saved: 0,
        error: err.message,
      });
    });
  });
}

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
   * Spawns a Python subprocess to run the scraper and write results to wie.db
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

        const result = await executeScraper(scraper);

        return {
          success: result.success,
          scraper,
          results_fetched: result.results_fetched,
          results_saved: result.results_saved,
          error: result.error,
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
    const scrapers = await Promise.all(
      VALID_SCRAPERS.map(async (name) => {
        const metadata = (await db.getScraperMetadata(name)) as any;
        return {
          name,
          last_run: metadata?.last_run || null,
          last_successful_run: metadata?.last_successful_run || null,
          error_count: metadata?.error_count || 0,
          last_error: metadata?.last_error || null,
          results_count: metadata?.results_count || 0,
        };
      })
    );

    return { scrapers };
  }),
});
