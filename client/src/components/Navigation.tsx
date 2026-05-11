import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { TrendingUp, Search, Map, Heart } from "lucide-react";

export default function Navigation() {
  const [location, navigate] = useLocation();

  const isActive = (path: string) => location === path;

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <TrendingUp className="w-6 h-6 text-blue-600" />
            <span className="font-bold text-lg text-slate-900">WIE</span>
          </button>

          {/* Nav Links */}
          <div className="flex items-center gap-1">
            <Button
              variant={isActive("/") ? "default" : "ghost"}
              onClick={() => navigate("/")}
              className="gap-2"
            >
              <TrendingUp className="w-4 h-4" />
              Dashboard
            </Button>

            <Button
              variant={isActive("/signals") ? "default" : "ghost"}
              onClick={() => navigate("/signals")}
              className="gap-2"
            >
              <Search className="w-4 h-4" />
              Signals
            </Button>

            <Button
              variant={isActive("/watchlist") ? "default" : "ghost"}
              onClick={() => navigate("/watchlist")}
              className="gap-2"
            >
              <Heart className="w-4 h-4" />
              Watchlist
            </Button>
          </div>

          {/* Right side - Status/User */}
          <div className="flex items-center gap-2">
            <div className="text-xs text-slate-600">
              <span className="inline-block w-2 h-2 bg-green-500 rounded-full mr-1"></span>
              Scheduler Active
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
