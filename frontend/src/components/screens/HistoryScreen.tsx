/**
 * History Screen
 * Browse past detections with date filters
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { Detection } from '../../types';
import { DetectionCard } from '../DetectionCard';
import './Screens.css';

interface DetectionsResponse {
  detections: Detection[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

async function fetchDetections(page: number, limit: number): Promise<DetectionsResponse> {
  const response = await fetch(`/api/detections?page=${page}&limit=${limit}`);
  if (!response.ok) throw new Error('Failed to fetch detections');
  return response.json();
}

const PAGE_SIZE = 20;

export function HistoryScreen() {
  const [page, setPage] = useState(1);
  
  const { data, isLoading, isError, isFetching } = useQuery({
    queryKey: ['detections', 'history', page],
    queryFn: () => fetchDetections(page, PAGE_SIZE),
    staleTime: 30_000,
  });

  const detections = data?.detections ?? [];
  const total = data?.total ?? 0;
  const hasMore = data?.has_more ?? false;
  const totalPages = Math.ceil(total / PAGE_SIZE);

  // Build ISO8601 from date + time since API returns null
  const enrichDetection = (d: Detection): Detection => {
    if (!d.iso8601 && d.date && d.time) {
      return { ...d, iso8601: `${d.date}T${d.time}` };
    }
    return d;
  };

  return (
    <div className="screen screen--history">
      <div className="history-header">
        <h2 className="screen__title">Detection History</h2>
        <span className="history-count">{total.toLocaleString()} total</span>
      </div>
      
      {isLoading && page === 1 && (
        <div className="history-loading">Loading...</div>
      )}
      
      {isError && (
        <div className="screen__placeholder">
          <p className="screen__text">Failed to load history</p>
        </div>
      )}
      
      {detections.length > 0 && (
        <div className="history-list">
          {detections.map((detection) => (
            <DetectionCard
              key={detection.id}
              detection={enrichDetection(detection)}
              ageCategory="recent"
            />
          ))}
        </div>
      )}
      
      {/* Pagination */}
      {totalPages > 1 && (
        <div className="history-pagination">
          <button
            className="history-pagination__btn"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1 || isFetching}
          >
            ← Previous
          </button>
          <span className="history-pagination__info">
            Page {page} of {totalPages}
          </span>
          <button
            className="history-pagination__btn"
            onClick={() => setPage(p => hasMore ? p + 1 : p)}
            disabled={!hasMore || isFetching}
          >
            Next →
          </button>
        </div>
      )}
      
      {isFetching && page > 1 && (
        <div className="history-loading">Loading more...</div>
      )}
    </div>
  );
}
