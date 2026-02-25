/**
 * SSE Provider Component
 * Manages connection status and event stream state
 */

import { useEffect, useState, useRef, type ReactNode } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { SSEContext } from './SSEContext';
import type { Detection } from '../types';

interface SSEProviderProps {
  children: ReactNode;
  eventSourceUrl?: string;
}

export function SSEProvider({ children, eventSourceUrl = '/api/events' }: SSEProviderProps) {
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'reconnecting' | 'disconnected'>('disconnected');
  const queryClient = useQueryClient();
  const eventSourceRef = useRef<EventSource | null>(null);
  const seenIdsRef = useRef(new Set<number>());
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const connect = () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      setConnectionStatus('reconnecting');

      const es = new EventSource(eventSourceUrl);
      eventSourceRef.current = es;

      es.onopen = () => {
        setConnectionStatus('connected');
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      es.onerror = () => {
        setConnectionStatus('disconnected');
        es.close();
        
        // Auto-reconnect after 3 seconds
        if (!reconnectTimeoutRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectTimeoutRef.current = null;
            connect();
          }, 3000);
        }
      };

      es.addEventListener('detection', (e: MessageEvent) => {
        try {
          const detection: Detection = JSON.parse(e.data);

          // Deduplicate by id
          if (seenIdsRef.current.has(detection.id)) return;
          seenIdsRef.current.add(detection.id);

          // Prepend to live feed cache
          queryClient.setQueryData<{ detections: Detection[] }>(
            ['detections', 'live'],
            (old) => ({ detections: [detection, ...(old?.detections ?? [])] })
          );

          // Mark related queries stale
          queryClient.invalidateQueries({ queryKey: ['summary', 'today'] });
          queryClient.invalidateQueries({ queryKey: ['species', 'today'] });
        } catch {
          // Silently ignore parse errors
        }
      });

      // Heartbeat handling - just confirms connection is alive
      es.addEventListener('heartbeat', () => {
        // Connection is alive, no action needed
      });
    };

    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };
  }, [eventSourceUrl, queryClient]);

  return (
    <SSEContext.Provider value={{ connectionStatus }}>
      {children}
    </SSEContext.Provider>
  );
}
