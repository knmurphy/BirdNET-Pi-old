import { useState, useCallback, useRef, useEffect } from 'react';

export function useAudio(_detectionId: number, fileName: string) {
	const [playing, setPlaying] = useState(false);
	const audioRef = useRef<HTMLAudioElement | null>(null);
	const audioUrl = `/api/audio/${encodeURIComponent(fileName)}`;

	// Cleanup on unmount
	useEffect(() => {
		return () => {
			if (audioRef.current) {
				audioRef.current.pause();
				audioRef.current = null;
			}
		};
	}, []);

	const toggle = useCallback(() => {
		if (!audioRef.current) {
			audioRef.current = new Audio(audioUrl);
			audioRef.current.onended = () => {
				setPlaying(false);
			};
			audioRef.current.onerror = () => {
				console.error('Audio playback error');
				setPlaying(false);
			};
		}

		if (playing) {
			audioRef.current.pause();
			audioRef.current.currentTime = 0;
			setPlaying(false);
		} else {
			audioRef.current.play().catch((err) => {
				console.error('Audio play failed:', err);
				setPlaying(false);
			});
			setPlaying(true);
		}
	}, [audioUrl, playing]);

	return { audioUrl, playing, toggle };
}
