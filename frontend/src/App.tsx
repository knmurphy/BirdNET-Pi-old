/**
 * Field Station OS - Main App Component
 * 
 * App structure with routing and providers:
 * - QueryClientProvider (TanStack Query)
 * - SSEContext.Provider (connection status)
 * - BrowserRouter (routing)
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { SSEProvider } from './contexts/SSEProvider';
import { Header } from './components/layout/Header';
import { TabBar } from './components/layout/TabBar';
import { LiveScreen } from './components/screens/LiveScreen';
import { SpeciesScreen } from './components/screens/SpeciesScreen';
import { SpeciesStatsScreen } from './components/screens/SpeciesStatsScreen';
import { HistoryScreen } from './components/screens/HistoryScreen';
import { StatsScreen } from './components/screens/StatsScreen';
import { SettingsScreen } from './components/screens/SettingsScreen';

import './App.css';

// Create query client with default options
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000, // 30 seconds
      gcTime: 5 * 60_000, // 5 minutes (formerly cacheTime)
      retry: 2,
      refetchOnWindowFocus: true,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <SSEProvider>
        <BrowserRouter>
          <div className="app">
            <Header stationName="Field Station" />
            <main className="app__main">
              <Routes>
                <Route path="/" element={<LiveScreen />} />
                <Route path="/species" element={<SpeciesScreen />} />
                <Route path="/species-stats" element={<SpeciesStatsScreen />} />
                <Route path="/history" element={<HistoryScreen />} />
                <Route path="/stats" element={<StatsScreen />} />
                <Route path="/settings" element={<SettingsScreen />} />
              </Routes>
            </main>
            <TabBar />
          </div>
        </BrowserRouter>
      </SSEProvider>
    </QueryClientProvider>
  );
}

export default App;
