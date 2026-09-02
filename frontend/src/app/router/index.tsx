import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Header, Footer } from "../../shared/ui/Header";
import { ExplorePage } from "../../pages/explore/ExplorePage";
import { DistrictDetailPage } from "../../pages/district/DistrictDetailPage";
import { ComparePage } from "../../pages/compare/ComparePage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60 * 5, // 5 minutes
    },
  },
});

export const AppRouter: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-[#f8f7f2] text-black">
          <Header />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Navigate to="/explore" replace />} />
              <Route path="/explore" element={<ExplorePage />} />
              <Route path="/district/:tradeAreaCode" element={<DistrictDetailPage />} />
              <Route path="/compare" element={<ComparePage />} />
              <Route path="*" element={<Navigate to="/explore" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
};
