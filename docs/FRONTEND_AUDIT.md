# React Frontend Audit — Gaps, Bugs & Polish

**Date:** 2026-02-28  
**Scope:** New React frontend (Live, Species, Info screens)

---

## Critical Fixes

### 1. Tab order — Info should be last
**Current:** Live | Info | Species  
**Desired:** Live | Species | Info  

Info is secondary; it should be on the far right. Update the `tabs` array order in `TabBar.tsx`.

### 2. Detection dimming doesn’t update over time
**Location:** `LiveScreen.tsx`, `DetectionCard.css`

Age-based dimming (medium: 75%, old: 50%) only updates when the component re-renders. Re-renders happen when:
- New detections arrive via SSE
- User navigates away and back

If no new detections arrive for 5+ minutes, older detections never transition from “recent” to “medium”/“old,” so they stay at full opacity.

**Fix:** Add a timer (e.g. every 30–60 seconds) to force a re-render so `getAgeCategory()` is recalculated, or move age calculation into a `useEffect` with an interval.

### 3. Undefined CSS variables
**Location:** `Screens.css`, `SpeciesRow.css`, `variables.css`

These variables are used but not defined in `variables.css`:

| Variable | Used in | Suggested mapping |
|----------|---------|--------------------|
| `--surface2` | Screens.css (3 places) | Add to variables, or use `--bg2` |
| `--text1` | Screens.css (2 places) | Use `--text` |
| `--text-muted` | Screens.css | Use `--text3` |
| `--color-text-primary` | Screens.css (Info section) | Use `--text` |
| `--color-text-secondary` | Screens.css | Use `--text2` |
| `--color-surface-secondary` | Screens.css | Use `--bg2` |
| `--color-accent-primary` | SpeciesRow.css | Use `--accent` |

### 4. Button class mismatch
**Location:** `InfoScreen.tsx`, `global.css`

InfoScreen uses `className="button button--primary"` but global.css defines `button.primary` (single class). Retry buttons won’t get primary styling.

**Fix:** Use `className="primary"` or add `.button--primary` to global.css.

### 5. Species chart days selector doesn’t work
**Location:** `SpeciesChartDialog.tsx`

`handleDaysChange` fetches new data, calls `onClose()`, and dispatches `open-chart`. No component listens for `open-chart`, so the dialog closes and the new data is discarded. Changing the days dropdown has no visible effect.

**Fix:** Either:
- Pass an `onDaysChange` callback that updates chart data and keeps the dialog open, or
- Add a listener for `open-chart` and reopen the dialog with the new species data.

---

## Bugs & Inconsistencies

### 6. Duplicate detections on Live page
**Location:** `LiveScreen.tsx`

“Most Recent” shows `detections.slice(0, 4)` and “Activity” shows `detections.slice(0, 100)`. The same 4 cards appear in both sections.

**Fix:** Either remove “Most Recent” and rely on “Activity,” or show only the 4 most recent in “Most Recent” and exclude them from “Activity” (e.g. `detections.slice(4, MAX_VISIBLE_DETECTIONS + 4)` in Activity).

### 7. Emoji used as icons (project rule violation)
**Location:** `LiveScreen.tsx`, `SpeciesScreen.tsx`

AGENTS.md: “Do NOT use emoji as icons. Use SVG icons.”

- `LiveScreen` EmptyState: `◉`
- `LiveScreen` ErrorState: `⚠`
- `SpeciesScreen` empty state: `🐦`

**Fix:** Replace with SVG icons (e.g. circle, alert triangle, bird outline).

### 8. Delete button icon is unclear
**Location:** `DetectionCard.tsx`

The delete button uses a custom SVG (circle + lines) that doesn’t read as “trash.” Consider a standard trash can icon.

### 9. Coordinates assume Northern/Western hemisphere
**Location:** `InfoScreen.tsx`

```tsx
<span>{settings.latitude.toFixed(4)}°N, {settings.longitude.toFixed(4)}°W</span>
```

Southern latitudes and Eastern longitudes would be wrong. Use sign or separate N/S and E/W based on value.

### 10. TabBar comment says “5 tabs”
**Location:** `TabBar.tsx`

Comment says “Fixed bottom navigation with 5 tabs” but there are 3 tabs. Update the comment.

---

## Polish & UX

### 11. Live page section padding
**Location:** `Screens.css`

`live-activity__title` has no left/right padding; the “Activity” heading may align poorly with the feed. Add padding to match `.live-feed` (e.g. `var(--space-4)`).

### 12. Info screen loading vs error layout
**Location:** `InfoScreen.tsx`

Loading shows a grid of skeletons; error shows a centered block. Consider consistent vertical centering for both.

### 13. Chart dialog close button
**Location:** `SpeciesChartDialog.tsx`, `ImageModal.tsx`, `FlickrAttributionModal.tsx`

Close buttons use plain “X” text. Consider an SVG close icon for consistency with `ImageModal`.

### 14. Station name is hardcoded
**Location:** `App.tsx`

`<Header stationName="Field Station" />` is hardcoded. Consider fetching from settings or config.

### 15. No pull-to-refresh on mobile
**Location:** Live, Species, Info screens

No pull-to-refresh for manual refresh on mobile. Consider adding for Live and Species.

### 16. Live feed scroll position
**Location:** `LiveScreen.tsx`

When new detections arrive, the list grows at the top. Users may want to stay at the top or have an option to “scroll to latest.”

### 17. Species “New” badge contrast
**Location:** `SpeciesRow.css`

`species-badge--new` uses `var(--color-accent-primary)` (undefined) and `color: white`. With `--accent`, contrast may be low in light theme. Verify WCAG contrast.

### 18. Missing loading state for map
**Location:** `InfoScreen.tsx`

Map shows “Loading map...” while `useMapImage` fetches. Consider a skeleton or spinner for consistency with other loading states.

---

## Summary

| Category | Count |
|----------|-------|
| Critical fixes | 5 |
| Bugs & inconsistencies | 5 |
| Polish & UX | 8 |

**Suggested order of work:**
1. Tab order (quick)
2. CSS variables (prevents broken styles)
3. Button class fix
4. Detection dimming timer
5. Chart days selector
6. Duplicate detections
7. Emoji → SVG icons
8. Remaining polish items
