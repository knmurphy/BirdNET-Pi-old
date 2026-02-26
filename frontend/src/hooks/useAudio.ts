import { useState, useCallback } from 'react';

export function useAudio(_detectionId: number, fileName: string) {
	const [playing, setPlaying] = useState(false);
	const audioUrl = `/api/audio/${encodeURIComponent(fileName)}`;

	const toggle = useCallback(() => {
		setPlaying((p) => !p);
		// Actual audio element handling would go here
	}, []);

	return { audioUrl, playing, toggle };
}
