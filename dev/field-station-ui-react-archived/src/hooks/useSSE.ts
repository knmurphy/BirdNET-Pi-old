import { useEffect, useRef, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { Detection, ConnectionStatus } from '../types';

export function useSSE() {
	const queryClient = useQueryClient();
	const seenIds = useRef(new Set<number>());
	const [status, setStatus] = useState<ConnectionStatus>('reconnecting');
	const reconnectTimeoutRef = useRef<number | null>(null);

	useEffect(() => {
		const es = new EventSource('/api/events');

		// Connection opened
		es.onopen = () => {
			setStatus('connected');
			if (reconnectTimeoutRef.current) {
				clearTimeout(reconnectTimeoutRef.current);
				reconnectTimeoutRef.current = null;
			}
		};

		// Handle detection events
		es.addEventListener('detection', (e) => {
			const detection: Detection = JSON.parse(e.data);

			// Deduplicate by id
			if (seenIds.current.has(detection.id)) return;
			seenIds.current.add(detection.id);

			// Prepend to live feed cache
			queryClient.setQueryData<{ detections: Detection[] }>(
				['detections', 'live'],
				(old) => ({ detections: [detection, ...(old?.detections ?? [])] })
			);

			// Invalidate summary queries
			queryClient.invalidateQueries({ queryKey: ['summary', 'today'] });
			queryClient.invalidateQueries({ queryKey: ['species', 'today'] });
		});

		// Handle errors/disconnect
		es.onerror = () => {
			setStatus('reconnecting');
			// Set disconnected after 5s of reconnecting
			reconnectTimeoutRef.current = window.setTimeout(() => {
				setStatus('disconnected');
			}, 5000);
		};

		return () => {
			es.close();
			if (reconnectTimeoutRef.current) {
				clearTimeout(reconnectTimeoutRef.current);
			}
		};
	}, [queryClient]);

	return { status };
}
