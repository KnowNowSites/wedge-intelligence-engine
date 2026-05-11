import { z } from "zod";
import { publicProcedure, router } from "../_core/trpc";

// Mock data - replace with database queries
const MOCK_WEDGES = [
  {
    id: "1",
    wedge_name: "Construction Permit Automation",
    wedge_score: 8.5,
    detector_source: "pain_signal",
    enterprise_value: "high",
    complexity: "medium",
    mrr_timeline: { to_10k_mrr_months: 6, to_100k_mrr_months: 18 },
    scoring: {
      pain_score: 9.0,
      spend_potential: 8.5,
      growth_rate: 7.8,
      expandability: 8.2,
      distribution_score: 7.5,
      competition_score: 4.0,
      capital_required: 5.0,
      regulatory_friction: 6.0,
    },
    evidence: [
      {
        source: "reddit",
        count: 23,
        examples: [
          "Permit process is completely manual and takes 3-6 months",
          "No software exists that handles the entire workflow",
        ],
      },
    ],
  },
  {
    id: "2",
    wedge_name: "Healthcare Compliance Software",
    wedge_score: 8.2,
    detector_source: "regulation_change",
    enterprise_value: "very_high",
    complexity: "high",
    mrr_timeline: { to_10k_mrr_months: 9, to_100k_mrr_months: 24 },
    scoring: {
      pain_score: 8.5,
      spend_potential: 9.0,
      growth_rate: 8.2,
      expandability: 7.8,
      distribution_score: 7.0,
      competition_score: 6.0,
      capital_required: 7.0,
      regulatory_friction: 8.5,
    },
    evidence: [],
  },
];

const MOCK_SIGNALS = [
  {
    id: "1",
    source: "reddit",
    type: "pain_signal",
    title: "Permit process is completely manual",
    description: "User frustrated with 6-month manual permit approval process",
    date: "2024-05-10",
    score: 9.2,
    url: "https://reddit.com/r/construction/...",
    metadata: { subreddit: "r/construction", upvotes: 234 },
  },
];

const MOCK_WATCHLIST = [
  {
    id: "1",
    wedge_name: "Construction Permit Automation",
    wedge_score: 8.5,
    status: "investigating",
    notes: "Reached out to 3 permit agencies. High interest.",
    date_added: "2024-04-15",
    last_updated: "2024-05-10",
  },
];

export const wedgesRouter = router({
  /**
   * Get all wedges with optional filtering and sorting
   */
  list: publicProcedure
    .input(
      z.object({
        search: z.string().optional(),
        detector: z.string().optional(),
        complexity: z.string().optional(),
        sortBy: z.enum(["score", "mrr", "value"]).optional().default("score"),
      })
    )
    .query(async ({ input }) => {
      // TODO: Query from database using SQLite
      // const db = await getDb();
      // const wedges = await db.query("SELECT * FROM wedge_profiles WHERE ...");

      let wedges = [...MOCK_WEDGES];

      // Filter
      if (input.search) {
        const search = input.search.toLowerCase();
        wedges = wedges.filter(
          (w) =>
            w.wedge_name.toLowerCase().includes(search) ||
            w.detector_source.toLowerCase().includes(search)
        );
      }

      if (input.detector && input.detector !== "all") {
        wedges = wedges.filter((w) => w.detector_source === input.detector);
      }

      if (input.complexity && input.complexity !== "all") {
        wedges = wedges.filter((w) => w.complexity === input.complexity);
      }

      // Sort
      if (input.sortBy === "score") {
        wedges.sort((a, b) => b.wedge_score - a.wedge_score);
      } else if (input.sortBy === "mrr") {
        wedges.sort(
          (a, b) =>
            a.mrr_timeline.to_10k_mrr_months - b.mrr_timeline.to_10k_mrr_months
        );
      }

      return { wedges, total: wedges.length };
    }),

  /**
   * Get a single wedge by ID
   */
  get: publicProcedure
    .input(z.object({ id: z.string() }))
    .query(async ({ input }) => {
      // TODO: Query from database
      const wedge = MOCK_WEDGES.find((w) => w.id === input.id);
      if (!wedge) {
        throw new Error(`Wedge ${input.id} not found`);
      }
      return wedge;
    }),

  /**
   * Get signals for a wedge
   */
  signals: publicProcedure
    .input(
      z.object({
        wedgeId: z.string(),
        source: z.string().optional(),
        type: z.string().optional(),
      })
    )
    .query(async ({ input }) => {
      // TODO: Query from database
      let signals = [...MOCK_SIGNALS];

      if (input.source) {
        signals = signals.filter((s) => s.source === input.source);
      }

      if (input.type) {
        signals = signals.filter((s) => s.type === input.type);
      }

      return { signals, total: signals.length };
    }),

  /**
   * Get all signals for explorer
   */
  exploreSignals: publicProcedure
    .input(
      z.object({
        search: z.string().optional(),
        source: z.string().optional(),
        type: z.string().optional(),
        sortBy: z.enum(["score", "date"]).optional().default("score"),
      })
    )
    .query(async ({ input }) => {
      // TODO: Query from database
      let signals = [...MOCK_SIGNALS];

      if (input.search) {
        const search = input.search.toLowerCase();
        signals = signals.filter(
          (s) =>
            s.title.toLowerCase().includes(search) ||
            s.description.toLowerCase().includes(search)
        );
      }

      if (input.source && input.source !== "all") {
        signals = signals.filter((s) => s.source === input.source);
      }

      if (input.type && input.type !== "all") {
        signals = signals.filter((s) => s.type === input.type);
      }

      if (input.sortBy === "score") {
        signals.sort((a, b) => b.score - a.score);
      } else {
        signals.sort(
          (a, b) =>
            new Date(b.date).getTime() - new Date(a.date).getTime()
        );
      }

      return { signals, total: signals.length };
    }),

  /**
   * Get watchlist
   */
  watchlist: publicProcedure.query(async () => {
    // TODO: Query from database for current user
    return { items: MOCK_WATCHLIST, total: MOCK_WATCHLIST.length };
  }),

  /**
   * Add to watchlist
   */
  addToWatchlist: publicProcedure
    .input(
      z.object({
        wedgeId: z.string(),
        notes: z.string().optional(),
      })
    )
    .mutation(async ({ input }) => {
      // TODO: Insert into watchlist table
      return { success: true, message: "Added to watchlist" };
    }),

  /**
   * Update watchlist item
   */
  updateWatchlistItem: publicProcedure
    .input(
      z.object({
        id: z.string(),
        status: z.enum(["watching", "investigating", "building", "passed"]),
        notes: z.string(),
      })
    )
    .mutation(async ({ input }) => {
      // TODO: Update watchlist table
      return { success: true, message: "Updated watchlist item" };
    }),

  /**
   * Remove from watchlist
   */
  removeFromWatchlist: publicProcedure
    .input(z.object({ id: z.string() }))
    .mutation(async ({ input }) => {
      // TODO: Delete from watchlist table
      return { success: true, message: "Removed from watchlist" };
    }),

  /**
   * Export watchlist as CSV
   */
  exportWatchlist: publicProcedure.query(async () => {
    // TODO: Query watchlist and format as CSV
    const items = MOCK_WATCHLIST;
    const headers = [
      "Wedge Name",
      "Score",
      "Status",
      "Notes",
      "Date Added",
      "Last Updated",
    ];
    const rows = items.map((item) => [
      item.wedge_name,
      item.wedge_score,
      item.status,
      item.notes,
      item.date_added,
      item.last_updated,
    ]);

    const csv = [
      headers.join(","),
      ...rows.map((row) =>
        row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")
      ),
    ].join("\n");

    return { csv, filename: `watchlist-${new Date().toISOString().split("T")[0]}.csv` };
  }),
});
