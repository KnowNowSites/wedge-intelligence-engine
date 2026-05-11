import { useState, useMemo } from "react";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, ExternalLink } from "lucide-react";

interface Signal {
  id: string;
  source: string;
  type: string;
  title: string;
  description: string;
  date: string;
  score: number;
  url?: string;
  metadata: Record<string, any>;
}

// Mock data
const MOCK_SIGNALS: Signal[] = [
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
  {
    id: "2",
    source: "hackernews",
    type: "pain_signal",
    title: "Why doesn't someone build a permit automation tool?",
    description: "HN discussion about lack of permit automation software",
    date: "2024-05-09",
    score: 8.7,
    url: "https://news.ycombinator.com/item?id=...",
    metadata: { thread_type: "ask_hn", score: 156 },
  },
  {
    id: "3",
    source: "app_store",
    type: "incumbent_weakness",
    title: "Competitor app has terrible UX",
    description: "1-star review criticizing competitor's user interface",
    date: "2024-05-08",
    score: 7.5,
    metadata: { app_name: "PermitHub", rating: 1 },
  },
  {
    id: "4",
    source: "google_trends",
    type: "distribution_gap",
    title: "Permit automation searches up 250%",
    description: "Google Trends shows breakout growth in permit automation searches",
    date: "2024-05-07",
    score: 8.9,
    metadata: { trend_score: 85, is_breakout: true },
  },
  {
    id: "5",
    source: "job_postings",
    type: "margin_expansion",
    title: "156 permit coordinator positions open",
    description: "Indeed shows high demand for manual permit coordination roles",
    date: "2024-05-06",
    score: 8.1,
    metadata: { industry: "construction", job_count: 156 },
  },
  {
    id: "6",
    source: "sec_filings",
    type: "regulation_change",
    title: "New permit requirements announced",
    description: "SEC filing mentions new regulatory compliance requirements",
    date: "2024-05-05",
    score: 7.8,
    metadata: { company: "BuildCorp Inc", industry_code: "1600" },
  },
];

export default function SignalExplorer() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterSource, setFilterSource] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");
  const [sortBy, setSortBy] = useState<"score" | "date">("score");

  const filteredAndSortedSignals = useMemo(() => {
    let filtered = MOCK_SIGNALS.filter((signal) => {
      const matchesSearch =
        signal.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        signal.description.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesSource = filterSource === "all" || signal.source === filterSource;
      const matchesType = filterType === "all" || signal.type === filterType;

      return matchesSearch && matchesSource && matchesType;
    });

    // Sort
    filtered.sort((a, b) => {
      if (sortBy === "score") {
        return b.score - a.score;
      } else {
        return new Date(b.date).getTime() - new Date(a.date).getTime();
      }
    });

    return filtered;
  }, [searchTerm, filterSource, filterType, sortBy]);

  const sources = Array.from(new Set(MOCK_SIGNALS.map((s) => s.source)));
  const types = Array.from(new Set(MOCK_SIGNALS.map((s) => s.type)));

  const getSourceColor = (source: string) => {
    const colors: Record<string, string> = {
      reddit: "bg-orange-100 text-orange-800",
      hackernews: "bg-amber-100 text-amber-800",
      app_store: "bg-blue-100 text-blue-800",
      google_trends: "bg-purple-100 text-purple-800",
      job_postings: "bg-green-100 text-green-800",
      sec_filings: "bg-red-100 text-red-800",
    };
    return colors[source] || "bg-slate-100 text-slate-800";
  };

  const getTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      pain_signal: "🔴",
      incumbent_weakness: "📉",
      distribution_gap: "📊",
      margin_expansion: "💰",
      regulation_change: "⚖️",
      emerging_category: "🌱",
      geographic_wedge: "🌍",
    };
    return icons[type] || "📌";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Signal Explorer</h1>
          <p className="text-slate-600">
            Browse raw signals from all data sources that feed the wedge detection engine
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-slate-200">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="lg:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                <Input
                  placeholder="Search signals..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Sort */}
            <Select value={sortBy} onValueChange={(v) => setSortBy(v as any)}>
              <SelectTrigger>
                <SelectValue placeholder="Sort by..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="score">Highest Score</SelectItem>
                <SelectItem value="date">Most Recent</SelectItem>
              </SelectContent>
            </Select>

            {/* Source Filter */}
            <Select value={filterSource} onValueChange={setFilterSource}>
              <SelectTrigger>
                <SelectValue placeholder="All sources" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sources</SelectItem>
                {sources.map((s) => (
                  <SelectItem key={s} value={s}>
                    {s.replace(/_/g, " ")}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Type Filter */}
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger>
                <SelectValue placeholder="All types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {types.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t.replace(/_/g, " ")}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-4 text-sm text-slate-600">
          Showing {filteredAndSortedSignals.length} of {MOCK_SIGNALS.length} signals
        </div>

        {/* Signals List */}
        <div className="space-y-4">
          {filteredAndSortedSignals.map((signal) => (
            <Card key={signal.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  {/* Icon */}
                  <div className="text-3xl mt-1">{getTypeIcon(signal.type)}</div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <div className="flex-1">
                        <h3 className="font-semibold text-slate-900 line-clamp-1">
                          {signal.title}
                        </h3>
                        <p className="text-sm text-slate-600 line-clamp-2 mt-1">
                          {signal.description}
                        </p>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <div className="text-2xl font-bold text-blue-600">
                          {signal.score.toFixed(1)}
                        </div>
                        <div className="text-xs text-slate-500">Signal Score</div>
                      </div>
                    </div>

                    {/* Metadata and Badges */}
                    <div className="flex flex-wrap items-center gap-2 mt-3">
                      <Badge className={getSourceColor(signal.source)}>
                        {signal.source.replace(/_/g, " ")}
                      </Badge>
                      <Badge variant="outline">{signal.type.replace(/_/g, " ")}</Badge>
                      <span className="text-xs text-slate-500">
                        {new Date(signal.date).toLocaleDateString()}
                      </span>

                      {/* Metadata display */}
                      {Object.entries(signal.metadata).map(([key, value]) => (
                        <span key={key} className="text-xs text-slate-500">
                          {key}: <span className="font-semibold">{String(value)}</span>
                        </span>
                      ))}

                      {/* External Link */}
                      {signal.url && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="ml-auto gap-1"
                          onClick={() => window.open(signal.url, "_blank")}
                        >
                          <ExternalLink className="w-4 h-4" />
                          View Source
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {filteredAndSortedSignals.length === 0 && (
          <Card className="text-center py-12">
            <Search className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600">No signals match your filters</p>
          </Card>
        )}
      </div>
    </div>
  );
}
