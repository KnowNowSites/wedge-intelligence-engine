import { z } from "zod";
import { publicProcedure, protectedProcedure, router } from "../_core/trpc";
import * as db from "../db";

export const wedgesRouter = router({
  list: publicProcedure
    .input(
      z.object({
        limit: z.number().default(50),
        offset: z.number().default(0),
        detector: z.string().optional(),
        complexity: z.string().optional(),
        search: z.string().optional(),
      }).optional()
    )
    .query(async ({ input }) => {
      const wedges = await db.getWedges({
        limit: input?.limit,
        offset: input?.offset,
        detector: input?.detector,
        complexity: input?.complexity,
        search: input?.search,
      });

      return {
        total: wedges.length,
        wedges: (wedges || []).map((w: any) => ({
          id: w.id,
          wedge_name: w.wedge_name,
          wedge_score: w.wedge_score,
          detector_source: w.detector_source,
          complexity: w.complexity,
          enterprise_value: w.enterprise_value,
          mrr_timeline: {
            to_10k_mrr_months: w.to_10k_mrr_months,
            to_100k_mrr_months: w.to_100k_mrr_months,
          },
        })),
      };
    }),

  get: publicProcedure
    .input(z.object({ wedge_id: z.string() }))
    .query(async ({ input }) => {
      const wedge = await db.getWedgeById(input.wedge_id);
      if (!wedge) {
        return null;
      }

      return {
        id: wedge.id,
        wedge_name: wedge.wedge_name,
        wedge_score: wedge.wedge_score,
        detector_source: wedge.detector_source,
        complexity: wedge.complexity,
        enterprise_value: wedge.enterprise_value,
        mrr_timeline: {
          to_10k_mrr_months: wedge.to_10k_mrr_months,
          to_100k_mrr_months: wedge.to_100k_mrr_months,
        },
        evidence: wedge.evidence_json,
        created_at: wedge.created_at,
      };
    }),

  signals: publicProcedure
    .input(z.object({ wedge_id: z.string() }))
    .query(async ({ input }) => {
      // Get signals related to this wedge
      const signals = await db.getSignals({ limit: 100 });
      return {
        signals: (signals || []).map((s: any) => ({
          id: s.id,
          source: s.source,
          type: s.type,
          title: s.title,
          description: s.description,
          score: s.score,
          url: s.url,
          metadata: s.metadata_json,
          created_at: s.created_at,
        })),
      };
    }),

  exploreSignals: publicProcedure
    .input(
      z.object({
        source: z.string().optional(),
        type: z.string().optional(),
        limit: z.number().default(50),
        offset: z.number().default(0),
      }).optional()
    )
    .query(async ({ input }) => {
      const signals = await db.getSignals({
        source: input?.source,
        type: input?.type,
        limit: input?.limit,
        offset: input?.offset,
      });

      return {
        total: signals.length,
        signals: (signals || []).map((signal: any) => ({
          id: signal.id,
          source: signal.source,
          type: signal.type,
          title: signal.title,
          description: signal.description,
          score: signal.score,
          url: signal.url,
          metadata: signal.metadata_json,
          created_at: signal.created_at,
        })),
      };
    }),

  addToWatchlist: protectedProcedure
    .input(z.object({ wedge_id: z.string(), notes: z.string().optional() }))
    .mutation(async ({ input }) => {
      const result = await db.addToWatchlist(input.wedge_id, input.notes);
      return result || { success: false };
    }),

  removeFromWatchlist: protectedProcedure
    .input(z.object({ watchlist_id: z.string() }))
    .mutation(async ({ input }) => {
      const success = await db.removeFromWatchlist(input.watchlist_id);
      return { success };
    }),

  watchlist: publicProcedure.query(async () => {
    const items = await db.getWatchlist();
    return {
      items: (items || []).map((item: any) => ({
        id: item.id,
        wedge_name: item.wedge_name,
        wedge_score: item.wedge_score,
        status: item.status,
        notes: item.notes,
        date_added: item.date_added,
      })),
    };
  }),

  updateWatchlistNotes: protectedProcedure
    .input(z.object({ watchlist_id: z.string(), notes: z.string() }))
    .mutation(async ({ input }) => {
      const updated = await db.updateWatchlistNotes(input.watchlist_id, input.notes);
      return updated || { success: false };
    }),

  exportWatchlistCSV: publicProcedure.query(async () => {
    const items = await db.getWatchlist();
    const csv = [
      ['Wedge Name', 'Score', 'Status', 'Notes', 'Date Added'].join(','),
      ...(items || []).map((item: any) =>
        [
          `"${item.wedge_name}"`,
          item.wedge_score,
          item.status,
          `"${item.notes || ''}"`,
          item.date_added,
        ].join(',')
      ),
    ].join('\n');

    return { csv };
  }),
});
