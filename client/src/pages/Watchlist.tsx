import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Download, Trash2, Edit2, Heart } from "lucide-react";

interface WatchlistItem {
  id: string;
  wedge_name: string;
  wedge_score: number;
  status: "watching" | "investigating" | "building" | "passed";
  notes: string;
  date_added: string;
  last_updated: string;
}

// Mock data
const MOCK_WATCHLIST: WatchlistItem[] = [
  {
    id: "1",
    wedge_name: "Construction Permit Automation",
    wedge_score: 8.5,
    status: "investigating",
    notes: "Reached out to 3 permit agencies. High interest. Need to validate pricing model.",
    date_added: "2024-04-15",
    last_updated: "2024-05-10",
  },
  {
    id: "2",
    wedge_name: "Healthcare Compliance Software",
    wedge_score: 8.2,
    status: "watching",
    notes: "Monitoring regulatory changes. HIPAA updates coming Q3 2024.",
    date_added: "2024-05-01",
    last_updated: "2024-05-08",
  },
  {
    id: "3",
    wedge_name: "Logistics Optimization",
    wedge_score: 7.9,
    status: "building",
    notes: "MVP in development. Beta launching with 5 logistics companies.",
    date_added: "2024-03-20",
    last_updated: "2024-05-10",
  },
  {
    id: "4",
    wedge_name: "Real Estate Valuation API",
    wedge_score: 7.5,
    status: "passed",
    notes: "Too much competition from Zillow API. Market already saturated.",
    date_added: "2024-04-01",
    last_updated: "2024-04-25",
  },
];

const STATUS_COLORS: Record<string, string> = {
  watching: "bg-blue-100 text-blue-800",
  investigating: "bg-yellow-100 text-yellow-800",
  building: "bg-green-100 text-green-800",
  passed: "bg-slate-100 text-slate-800",
};

export default function Watchlist() {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>(MOCK_WATCHLIST);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingNotes, setEditingNotes] = useState("");
  const [editingStatus, setEditingStatus] = useState<WatchlistItem["status"]>("watching");

  const handleEdit = (item: WatchlistItem) => {
    setEditingId(item.id);
    setEditingNotes(item.notes);
    setEditingStatus(item.status);
  };

  const handleSave = () => {
    if (editingId) {
      setWatchlist(
        watchlist.map((item) =>
          item.id === editingId
            ? {
                ...item,
                notes: editingNotes,
                status: editingStatus,
                last_updated: new Date().toISOString().split("T")[0],
              }
            : item
        )
      );
      setEditingId(null);
    }
  };

  const handleDelete = (id: string) => {
    setWatchlist(watchlist.filter((item) => item.id !== id));
  };

  const handleExportCSV = () => {
    const headers = ["Wedge Name", "Score", "Status", "Notes", "Date Added", "Last Updated"];
    const rows = watchlist.map((item) => [
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

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `watchlist-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const stats = {
    total: watchlist.length,
    watching: watchlist.filter((w) => w.status === "watching").length,
    investigating: watchlist.filter((w) => w.status === "investigating").length,
    building: watchlist.filter((w) => w.status === "building").length,
    passed: watchlist.filter((w) => w.status === "passed").length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <Heart className="w-8 h-8 text-red-600" />
            <h1 className="text-4xl font-bold text-slate-900">My Watchlist</h1>
          </div>
          <p className="text-slate-600">
            Track wedges you're investigating or building
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                Total Wedges
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">{stats.total}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-blue-600">
                Watching
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">{stats.watching}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-yellow-600">
                Investigating
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600">{stats.investigating}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-green-600">
                Building
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">{stats.building}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-600">
                Passed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-600">{stats.passed}</div>
            </CardContent>
          </Card>
        </div>

        {/* Export Button */}
        <div className="mb-6 flex justify-end">
          <Button onClick={handleExportCSV} className="gap-2">
            <Download className="w-4 h-4" />
            Export as CSV
          </Button>
        </div>

        {/* Table */}
        <Card>
          <CardHeader>
            <CardTitle>Tracked Wedges</CardTitle>
            <CardDescription>
              Manage your watchlist and track progress on each opportunity
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Wedge Name</TableHead>
                    <TableHead className="text-right">Score</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Last Updated</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {watchlist.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.wedge_name}</TableCell>
                      <TableCell className="text-right font-semibold">
                        {item.wedge_score.toFixed(1)}
                      </TableCell>
                      <TableCell>
                        <Badge className={STATUS_COLORS[item.status]}>
                          {item.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-slate-600">
                        {new Date(item.last_updated).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEdit(item)}
                              className="gap-1"
                            >
                              <Edit2 className="w-4 h-4" />
                              Edit
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-2xl">
                            <DialogHeader>
                              <DialogTitle>Edit Watchlist Item</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div>
                                <label className="text-sm font-medium text-slate-700">
                                  Wedge Name
                                </label>
                                <Input
                                  value={item.wedge_name}
                                  disabled
                                  className="mt-1"
                                />
                              </div>

                              <div>
                                <label className="text-sm font-medium text-slate-700">
                                  Status
                                </label>
                                <Select value={editingStatus} onValueChange={(v) => setEditingStatus(v as any)}>
                                  <SelectTrigger className="mt-1">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="watching">Watching</SelectItem>
                                    <SelectItem value="investigating">Investigating</SelectItem>
                                    <SelectItem value="building">Building</SelectItem>
                                    <SelectItem value="passed">Passed</SelectItem>
                                  </SelectContent>
                                </Select>
                              </div>

                              <div>
                                <label className="text-sm font-medium text-slate-700">
                                  Notes
                                </label>
                                <Textarea
                                  value={editingNotes}
                                  onChange={(e) => setEditingNotes(e.target.value)}
                                  placeholder="Add your notes here..."
                                  className="mt-1 min-h-24"
                                />
                              </div>

                              <div className="flex gap-2 justify-end">
                                <Button variant="outline">Cancel</Button>
                                <Button onClick={handleSave}>Save Changes</Button>
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(item.id)}
                          className="gap-1 text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                          Remove
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {/* Notes Column */}
        {watchlist.length > 0 && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>Notes & Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {watchlist.map((item) => (
                  <div key={item.id} className="border-b border-slate-200 pb-4 last:border-0">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-slate-900">{item.wedge_name}</h4>
                      <Badge className={STATUS_COLORS[item.status]}>
                        {item.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-700 bg-slate-50 p-3 rounded">
                      {item.notes}
                    </p>
                    <p className="text-xs text-slate-500 mt-2">
                      Added {new Date(item.date_added).toLocaleDateString()} • Updated{" "}
                      {new Date(item.last_updated).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
