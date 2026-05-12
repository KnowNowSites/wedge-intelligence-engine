# WIE Frontend - React Components

This directory contains the React 19 + Tailwind CSS frontend for the Wedge Intelligence Engine.

## Directory Structure

```
client/
├── src/
│   ├── pages/              # Page components (4 main views)
│   ├── components/         # Reusable UI components
│   ├── contexts/           # React contexts (theme, auth)
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utilities (tRPC client, helpers)
│   ├── App.tsx             # Main router and layout
│   ├── main.tsx            # React entry point
│   └── index.css            # Global styles and theme
├── public/                 # Static assets (favicon, robots.txt)
└── package.json            # Dependencies
```

## Pages (4 Main Views)

### 1. Dashboard (`/`)
**File:** `src/pages/Dashboard.tsx`

Main landing page showing ranked wedge opportunities.

**Features:**
- Ranked wedge cards (sorted by score, MRR, or value)
- Filters: detector source, complexity level, global search
- Sort controls: highest score, fastest to $10k MRR, highest value
- Quick stats: score, MRR timeline, enterprise value, complexity
- Click card to navigate to detail page

**Key Components:**
- `Card` - Wedge opportunity card with score badge
- `Select` - Filter and sort dropdowns
- `Input` - Search field
- `Badge` - Score and complexity indicators
- `Button` - "View Details" CTA

**Data Source:**
```typescript
const { data } = trpc.wedges.list.useQuery({
  search: searchTerm,
  detector: filterDetector,
  complexity: filterComplexity,
  sortBy: sortBy,
});
```

### 2. Wedge Detail (`/wedge/:id`)
**File:** `src/pages/WedgeDetail.tsx`

Full profile page for a single wedge opportunity.

**Features:**
- Key metrics: score, MRR timeline, enterprise value, complexity
- Tabs: Scoring Breakdown, Evidence, Expansion Map
- Scoring breakdown: 8 factors (pain, spend, growth, etc.)
- Evidence panel: signals from each source with examples
- Expansion map: adjacent markets, geographic, product, revenue opportunities
- Save to watchlist action

**Key Components:**
- `Tabs` - Tabbed interface for different views
- `Progress` - Score factor visualization
- `Card` - Evidence and expansion opportunity cards
- `Badge` - Source and type indicators
- `Button` - Save to watchlist CTA

**Data Source:**
```typescript
const { data: wedge } = trpc.wedges.get.useQuery({ id });
const { data: signals } = trpc.wedges.signals.useQuery({ wedgeId: id });
```

### 3. Signal Explorer (`/signals`)
**File:** `src/pages/SignalExplorer.tsx`

Browse raw signals from all data sources.

**Features:**
- Signal feed with title, description, score
- Filters: by source (Reddit, HN, App Store, etc.), by type (pain, regulation, etc.)
- Sort: by score or date
- External links to original sources
- Metadata display (upvotes, app name, etc.)

**Key Components:**
- `Input` - Search field
- `Select` - Source and type filters
- `Card` - Signal item with metadata
- `Badge` - Source and type badges
- `Button` - External link button

**Data Source:**
```typescript
const { data } = trpc.wedges.exploreSignals.useQuery({
  search: searchTerm,
  source: filterSource,
  type: filterType,
  sortBy: sortBy,
});
```

### 4. Watchlist (`/watchlist`)
**File:** `src/pages/Watchlist.tsx`

Track opportunities you're investigating or building.

**Features:**
- Stats dashboard: total, watching, investigating, building, passed
- Watchlist table with wedge name, score, status, last updated
- Edit modal: change status, add notes
- Notes panel: view all notes and progress
- CSV export: download watchlist for sharing

**Key Components:**
- `Table` - Watchlist items
- `Dialog` - Edit modal for status and notes
- `Badge` - Status indicators
- `Button` - Edit and delete actions
- `Textarea` - Notes field

**Data Source:**
```typescript
const { data: watchlist } = trpc.wedges.watchlist.useQuery();
const addMutation = trpc.wedges.addToWatchlist.useMutation();
const updateMutation = trpc.wedges.updateWatchlistItem.useMutation();
const exportMutation = trpc.wedges.exportWatchlist.useQuery();
```

## Navigation Component

**File:** `src/components/Navigation.tsx`

Sticky header with navigation links and scheduler status.

**Features:**
- WIE logo/brand
- Navigation links: Dashboard, Signals, Watchlist
- Active route highlighting
- Scheduler status indicator (green dot = active)

**Usage:**
```tsx
import Navigation from "@/components/Navigation";

<Navigation />
```

## Reusable Components

All components from `shadcn/ui` library are available in `src/components/ui/`:

### Layout Components
- `Card` - Container with header, content, footer
- `Tabs` - Tabbed interface
- `Dialog` - Modal dialog
- `Popover` - Floating popover

### Form Components
- `Input` - Text input
- `Select` - Dropdown select
- `Textarea` - Multi-line text
- `Button` - Button with variants (default, outline, ghost)
- `Badge` - Inline badge/label

### Data Display
- `Table` - Data table with header/body/rows
- `Progress` - Progress bar
- `Separator` - Visual divider

### Feedback
- `Toast` - Toast notifications (via Sonner)
- `Tooltip` - Hover tooltip

## Styling

### Global Theme
**File:** `src/index.css`

Defines CSS variables for colors, spacing, typography:
```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 0 0% 3.6%;
    --primary: 0 0% 9%;
    --primary-foreground: 0 0% 98%;
    /* ... more variables */
  }
}
```

### Tailwind CSS 4
All components use Tailwind utility classes:
- Spacing: `p-4`, `m-2`, `gap-3`
- Colors: `text-slate-900`, `bg-blue-50`
- Responsive: `md:grid-cols-2`, `lg:max-w-6xl`
- States: `hover:shadow-lg`, `focus:ring-2`

### Component Variants
shadcn/ui components support variants:
```tsx
<Button variant="default" size="lg">Primary</Button>
<Button variant="outline" size="sm">Secondary</Button>
<Button variant="ghost">Tertiary</Button>
```

## Custom Hooks

### useAuth()
**File:** `src/_core/hooks/useAuth.ts`

Get current user authentication state.

```typescript
const { user, loading, isAuthenticated, logout } = useAuth();

if (loading) return <Spinner />;
if (!isAuthenticated) return <LoginButton />;
return <Dashboard />;
```

### useTheme()
**File:** `src/contexts/ThemeContext.tsx`

Get and toggle theme (light/dark).

```typescript
const { theme, toggleTheme } = useTheme();

<button onClick={toggleTheme}>
  {theme === 'light' ? '🌙' : '☀️'}
</button>
```

## tRPC Integration

### Setup
**File:** `src/lib/trpc.ts`

tRPC client is pre-configured and ready to use:

```typescript
import { trpc } from "@/lib/trpc";
```

### Query Example
```typescript
const { data, isLoading, error } = trpc.wedges.list.useQuery({
  search: "permit",
  sortBy: "score",
});

if (isLoading) return <Spinner />;
if (error) return <Error message={error.message} />;
return <WedgeList wedges={data.wedges} />;
```

### Mutation Example
```typescript
const mutation = trpc.wedges.addToWatchlist.useMutation({
  onSuccess: () => {
    toast.success("Added to watchlist");
  },
  onError: (error) => {
    toast.error(error.message);
  },
});

<button onClick={() => mutation.mutate({ wedgeId: "1" })}>
  {mutation.isPending ? "Saving..." : "Save"}
</button>
```

### Optimistic Updates
```typescript
const mutation = trpc.wedges.updateWatchlistItem.useMutation({
  onMutate: async (newData) => {
    // Cancel outgoing refetches
    await trpc.useUtils().wedges.watchlist.cancel();
    
    // Snapshot previous data
    const previousData = trpc.useUtils().wedges.watchlist.getData();
    
    // Optimistically update cache
    trpc.useUtils().wedges.watchlist.setData(undefined, (old) => ({
      ...old,
      items: old.items.map((item) =>
        item.id === newData.id ? { ...item, ...newData } : item
      ),
    }));
    
    return { previousData };
  },
  onError: (err, newData, context) => {
    // Rollback on error
    if (context?.previousData) {
      trpc.useUtils().wedges.watchlist.setData(undefined, context.previousData);
    }
  },
  onSettled: () => {
    // Refetch after mutation
    trpc.useUtils().wedges.watchlist.invalidate();
  },
});
```

## Routing

**File:** `src/App.tsx`

Routes are defined using Wouter:

```typescript
<Switch>
  <Route path={"/"} component={Dashboard} />
  <Route path={"/wedge/:id"} component={WedgeDetail} />
  <Route path={"/signals"} component={SignalExplorer} />
  <Route path={"/watchlist"} component={Watchlist} />
  <Route path={"/404"} component={NotFound} />
  <Route component={NotFound} />
</Switch>
```

## Development Workflow

### Add a New Page

1. Create `src/pages/NewPage.tsx`:
```typescript
export default function NewPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      {/* Content */}
    </div>
  );
}
```

2. Add route in `src/App.tsx`:
```typescript
import NewPage from "./pages/NewPage";

<Route path={"/newpage"} component={NewPage} />
```

3. Add navigation link in `src/components/Navigation.tsx`:
```typescript
<Button
  variant={isActive("/newpage") ? "default" : "ghost"}
  onClick={() => navigate("/newpage")}
>
  New Page
</Button>
```

### Add a New Component

1. Create `src/components/MyComponent.tsx`:
```typescript
interface MyComponentProps {
  title: string;
  onClick: () => void;
}

export default function MyComponent({ title, onClick }: MyComponentProps) {
  return (
    <div className="p-4 bg-white rounded-lg">
      <h2 className="font-semibold">{title}</h2>
      <button onClick={onClick}>Click me</button>
    </div>
  );
}
```

2. Use in a page:
```typescript
import MyComponent from "@/components/MyComponent";

<MyComponent title="Hello" onClick={() => console.log("clicked")} />
```

## Performance Tips

1. **Memoization**: Use `useMemo` for expensive computations
```typescript
const filteredWedges = useMemo(() => {
  return wedges.filter(w => w.score > threshold);
}, [wedges, threshold]);
```

2. **Lazy Loading**: Use React.lazy for code splitting
```typescript
const Dashboard = lazy(() => import("./pages/Dashboard"));
```

3. **Image Optimization**: Use `manus-upload-file --webdev` for assets
```typescript
<img src="/manus-storage/image_a1b2c3d4.png" alt="Wedge" />
```

4. **Debouncing**: Debounce search input
```typescript
const [search, setSearch] = useState("");
const debouncedSearch = useMemo(
  () => debounce((value) => setSearch(value), 300),
  []
);
```

## Testing

### Unit Tests
**File:** `src/pages/Dashboard.test.tsx`

```typescript
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Dashboard from "./Dashboard";

describe("Dashboard", () => {
  it("renders wedge cards", () => {
    render(<Dashboard />);
    expect(screen.getByText("Construction Permit Automation")).toBeInTheDocument();
  });
});
```

### Run Tests
```bash
pnpm test
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Accessibility

All components follow WCAG 2.1 AA guidelines:
- Semantic HTML (`<button>`, `<nav>`, `<main>`)
- ARIA labels for icons
- Keyboard navigation (Tab, Enter, Escape)
- Focus indicators
- Color contrast ratios

## Build & Deployment

### Development
```bash
pnpm dev
```

Starts Vite dev server with HMR on http://localhost:5173

### Production Build
```bash
pnpm build
```

Creates optimized bundle in `dist/`

### Preview
```bash
pnpm preview
```

Preview production build locally

---

**For backend integration, see INTEGRATION_GUIDE.md**
