# Frontend Agent Guidelines (SEOUL DATA PLAYGROUND)

## Structure
- `src/pages/explore/ExplorePage.tsx`: Explore / Before selecting district (Reference Image 1).
- `src/pages/district/DistrictDetailPage.tsx`: District Detail / After selecting district (Reference Image 2).
- `src/pages/compare/ComparePage.tsx`: District comparison matrix (up to 3 districts).
- `src/shared/ui/Charts.tsx`: Custom Recharts components for rankings, time distribution, age/gender, and weekday trends.
- `src/shared/ui/Signals.tsx`: Neon signals, score pills, and status tags.
- `src/shared/api/client.ts`: Unified API client with automatic mock fallback.
- `src/shared/lib/store.ts`: Zustand store for comparison list state.

## Key Rules
- Font families: Pretendard for Korean headings/body, Space Grotesk / JetBrains Mono for metrics and timestamps.
- Zero unnecessary animations or glossy shadows; prioritize dense, legible, editorial data layout.
- Always verify routes `/explore`, `/district/:tradeAreaCode`, and `/compare`.
