import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, ExternalLink, Loader2 } from "lucide-react";
import { trpc } from "@/lib/trpc";
import { useMemo, useState } from "react";

interface Signal {
  id: string;
  source: string;
  type: string;
  title: string;
  description: string;
  score: number;
  url: string;
  metadata: Record<string, any>;
  created_at: string;
}

export default function SignalExplorer() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterSource, setFilterSource] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"score" | "date">("score");

  // Fetch real data from tRPC
  const { data, isLoading, error } = trpc.wedges.exploreSignals.useQuery({
    source: filterSource === "all" ? undefined : filterSource,
    type: filterType === "all" ? undefined : filterType,
    limit: 100,
  });

  const signals = data?.signals || [];

  const sources = Array.from(
    new Set(signals.map((s: any) => s.source))
  );

  const types = Array.from(
    new Set(signals.map((s: any) => s.type))
  );

  const getSourceColor = (source: string) => {
    switch (source) {
      case "reddit":
        return "bg-orange-100 text-orange-800";
      case "hackernews":
        return "bg-amber-100 text-amber-800";
      case "app_store":
        return "bg-blue-100 text-blue-800";
      case "play_store":
        return "bg-green-100 text-green-800";
      case "google_trends":
        return "bg-purple-100 text-purple-800";
      case "producthunt":
        return "bg-pink-100 text-pink-800";
      case "sec_filings":
        return "bg-red-100 text-red-800";
      case "job_postings":
        return "bg-cyan-100 text-cyan-800";
      case "yc":
        return "bg-indigo-100 text-indigo-800";
      case "openvc":
        return "bg-violet-100 text-violet-800";
      default:
        return "bg-slate-100 text-slate-800";
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "pain_signal":
        return "bg-red-50 text-red-700 border border-red-200";
      case "incumbent_weakness":
        return "bg-yellow-50 text-yellow-700 border border-yellow-200";
      case "emerging_category":
        return "bg-blue-50 text-blue-700 border border-blue-200";
      case "distribution_gap":
        return "bg-green-50 text-green-700 border border-green-200";
      case "regulation_change":
        return "bg-purple-50 text-purple-700 border border-purple-200";
      case "margin_expansion":
        return "bg-orange-50 text-orange-700 border border-orange-200";
      case "geographic_wedge":
        return "bg-pink-50 text-pink-700 border border-pink-200";
      default:
        return "bg-slate-50 text-slate-700 border border-slate-200";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Signal Explorer</h1>
          <p className="text-lg text-slate-600">Browse raw signals from all data sources</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-slate-200">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-3 w-4 h-4 text-slate-400" />
              <Input
                placeholder="Search signals..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Source Filter */}
            <Select value={filterSource} onValueChange={setFilterSource}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sources</SelectItem>
                {sources.map((source: any) => (
                  <SelectItem key={String(source)} value={String(source)}>
                    {String(source).replace(/_/g, " ")}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Type Filter */}
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {types.map((type: any) => (
                  <SelectItem key={String(type)} value={String(type)}>
                    {String(type).replace(/_/g, " ")}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Sort */}
            <Select value={sortBy} onValueChange={(value) => setSortBy(value as any)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="score">Highest Score</SelectItem>
                <SelectItem value="date">Most Recent</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Results */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
            <p className="text-slate-600">Loading signals...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-red-800">
            <p className="font-semibold">Error loading signals</p>
            <p className="text-sm mt-1">{error.message}</p>
          </div>
        ) : signals.length === 0 ? (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-12 text-center">
            <p className="text-slate-600 text-lg">No signals found matching your filters</p>
            <p className="text-slate-500 text-sm mt-2">Try adjusting your search or filters</p>
          </div>
        ) : (
          <>
            <p className="text-slate-600 mb-4">Showing {signals.length} signals</p>

            {/* Signal Feed */}
            <div className="space-y-4">
              {signals.map((signal: Signal) => (
                <Card
                  key={signal.id}
                  className="border-l-4 border-l-blue-400 hover:shadow-md transition-shadow cursor-pointer"
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <CardTitle className="text-base leading-tight">{signal.title}</CardTitle>
                        <CardDescription className="text-xs mt-2">
                          {signal.source.replace(/_/g, " ")} • {signal.created_at}
                        </CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getSourceColor(signal.source)}>
                          {signal.source.replace(/_/g, " ")}
                        </Badge>
                        <Badge className={getTypeColor(signal.type)}>
                          {signal.type.replace(/_/g, " ")}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-3">
                    <p className="text-sm text-slate-700">{signal.description}</p>

                    <div className="flex items-center justify-between pt-2 border-t">
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span>Score: <span className="font-bold text-slate-900">{signal.score.toFixed(1)}</span></span>
                        {signal.metadata && Object.keys(signal.metadata).length > 0 && (
                          <span>
                            {Object.entries(signal.metadata).map(([key, value]) => (
                              <span key={key} className="ml-2">
                                {key}: <span className="font-semibold">{String(value)}</span>
                              </span>
                            ))}
                          </span>
                        )}
                      </div>
                      {signal.url && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="gap-2 h-auto p-1"
                          onClick={() => window.open(signal.url, "_blank")}
                        >
                          <ExternalLink className="w-4 h-4" />
                          View
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
