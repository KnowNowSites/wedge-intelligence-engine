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
import { Download, Trash2, Edit2, Heart, Loader2 } from "lucide-react";
import { trpc } from "@/lib/trpc";
import { useState } from "react";
import { toast } from "sonner";

interface WatchlistItem {
  id: string;
  wedge_name: string;
  wedge_score: number;
  status: "watching" | "investigating" | "building" | "passed";
  notes: string;
  date_added: string;
  last_updated: string;
}

const STATUS_COLORS: Record<string, string> = {
  watching: "bg-blue-100 text-blue-800",
  investigating: "bg-yellow-100 text-yellow-800",
  building: "bg-green-100 text-green-800",
  passed: "bg-slate-100 text-slate-800",
};

export default function Watchlist() {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editStatus, setEditStatus] = useState<"watching" | "investigating" | "building" | "passed">("watching");
  const [editNotes, setEditNotes] = useState("");

  // Fetch real data from tRPC
  const { data, isLoading, error, refetch } = trpc.wedges.watchlist.useQuery();

  // Mutations
  const updateMutation = trpc.wedges.updateWatchlistNotes.useMutation({
    onSuccess: () => {
      toast.success("Watchlist item updated");
      setEditingId(null);
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.message);
    },
  });

  const deleteMutation = trpc.wedges.removeFromWatchlist.useMutation({
    onSuccess: () => {
      toast.success("Removed from watchlist");
      refetch();
    },
    onError: (error: any) => {
      toast.error(error.message);
    },
  });

  const exportMutation = trpc.wedges.exportWatchlistCSV.useQuery();

  const items = data?.items || [];

  const stats = {
    total: items.length,
    watching: items.filter((i: any) => i.status === "watching").length,
    investigating: items.filter((i: any) => i.status === "investigating").length,
    building: items.filter((i: any) => i.status === "building").length,
    passed: items.filter((i: any) => i.status === "passed").length,
  };

  const handleEdit = (item: any) => {
    setEditingId(item.id);
    setEditStatus(item.status as "watching" | "investigating" | "building" | "passed");
    setEditNotes(item.notes);
  };

  const handleSave = () => {
    if (!editingId) return;
    updateMutation.mutate({
      watchlist_id: editingId,
      notes: editNotes,
    });
  };

  const handleDelete = (id: string) => {
    if (confirm("Remove from watchlist?")) {
      deleteMutation.mutate({ watchlist_id: id });
    }
  };

  const handleExport = () => {
    if (exportMutation.data?.csv) {
      const blob = new Blob([exportMutation.data.csv], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "watchlist.csv";
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success("Watchlist exported");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Watchlist</h1>
          <p className="text-lg text-slate-600">Track opportunities you're investigating or building</p>
        </div>

        {/* Stats */}
        {!isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-600">Total</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-900">{stats.total}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-blue-600">Watching</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">{stats.watching}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-yellow-600">Investigating</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-yellow-600">{stats.investigating}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-green-600">Building</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">{stats.building}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-600">Passed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-slate-600">{stats.passed}</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Export Button */}
        <div className="mb-6 flex justify-end">
          <Button
            onClick={handleExport}
            variant="outline"
            size="sm"
            className="gap-2"
            disabled={items.length === 0}
          >
            <Download className="w-4 h-4" />
            Export CSV
          </Button>
        </div>

        {/* Results */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
            <p className="text-slate-600">Loading watchlist...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-red-800">
            <p className="font-semibold">Error loading watchlist</p>
            <p className="text-sm mt-1">{error.message}</p>
          </div>
        ) : items.length === 0 ? (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-12 text-center">
            <Heart className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-600 text-lg">Your watchlist is empty</p>
            <p className="text-slate-500 text-sm mt-2">Save opportunities from the dashboard to track them here</p>
          </div>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Tracked Opportunities</CardTitle>
              <CardDescription>Showing {items.length} items</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Wedge Name</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Added</TableHead>
                      <TableHead>Updated</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {items.map((item: any) => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{item.wedge_name}</TableCell>
                        <TableCell>
                          <Badge className="bg-green-100 text-green-800">
                            {item.wedge_score.toFixed(1)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className={STATUS_COLORS[item.status]}>
                            {item.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm text-slate-600">{item.date_added}</TableCell>
                        <TableCell className="text-sm text-slate-600">{item.last_updated}</TableCell>
                        <TableCell className="text-right">
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleEdit(item)}
                                className="gap-2"
                              >
                                <Edit2 className="w-4 h-4" />
                              </Button>
                            </DialogTrigger>
                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>Edit Watchlist Item</DialogTitle>
                              </DialogHeader>
                              <div className="space-y-4">
                                <div>
                                  <label className="text-sm font-medium text-slate-700">Status</label>
                                  <Select value={editStatus} onValueChange={(value) => setEditStatus(value as any)}>
                                    <SelectTrigger>
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
                                  <label className="text-sm font-medium text-slate-700">Notes</label>
                                  <Textarea
                                    value={editNotes}
                                    onChange={(e) => setEditNotes(e.target.value)}
                                    placeholder="Add notes about your investigation..."
                                    className="mt-1 min-h-24"
                                  />
                                </div>

                                <div className="flex gap-2 justify-end">
                                  <Button
                                    variant="outline"
                                    onClick={() => setEditingId(null)}
                                  >
                                    Cancel
                                  </Button>
                                  <Button
                                    onClick={handleSave}
                                    disabled={updateMutation.isPending}
                                  >
                                    {updateMutation.isPending ? "Saving..." : "Save"}
                                  </Button>
                                </div>
                              </div>
                            </DialogContent>
                          </Dialog>

                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(item.id)}
                            disabled={deleteMutation.isPending}
                            className="gap-2 text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Notes Section */}
        {items.length > 0 && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>Investigation Notes</CardTitle>
              <CardDescription>View and manage your research notes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {items
                  .filter((item: any) => item.notes)
                  .map((item: any) => (
                    <div key={item.id} className="border-l-4 border-l-blue-400 pl-4 py-2">
                      <p className="font-semibold text-slate-900">{item.wedge_name}</p>
                      <p className="text-sm text-slate-700 mt-1">{item.notes}</p>
                      <p className="text-xs text-slate-500 mt-2">
                        Updated: {item.last_updated}
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
