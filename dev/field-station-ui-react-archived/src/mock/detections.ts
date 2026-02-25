/**
 * Mock Detection Data
 * For development and testing of detection components
 */

import type { Detection } from '../types';

export const mockDetections: Detection[] = [
	{
		id: 1,
		com_name: 'Black-capped Chickadee',
		sci_name: 'Poecile atricapillus',
		confidence: 0.97,
		date: '2026-02-25',
		time: '07:42:11',
		iso8601: '2026-02-25T07:42:11-05:00',
		file_name: '2026-02-25/birdnet/2026-02-25T074211.wav',
		classifier: 'birdnet',
	},
	{
		id: 2,
		com_name: 'Northern Cardinal',
		sci_name: 'Cardinalis cardinalis',
		confidence: 0.92,
		date: '2026-02-25',
		time: '07:38:45',
		iso8601: '2026-02-25T07:38:45-05:00',
		file_name: '2026-02-25/birdnet/2026-02-25T073845.wav',
		classifier: 'birdnet',
	},
	{
		id: 3,
		com_name: 'American Robin',
		sci_name: 'Turdus migratorius',
		confidence: 0.78,
		date: '2026-02-25',
		time: '07:35:22',
		iso8601: '2026-02-25T07:35:22-05:00',
		file_name: '2026-02-25/birdnet/2026-02-25T073522.wav',
		classifier: 'birdnet',
	},
	{
		id: 4,
		com_name: 'Blue Jay',
		sci_name: 'Cyanocitta cristata',
		confidence: 0.89,
		date: '2026-02-25',
		time: '07:31:08',
		iso8601: '2026-02-25T07:31:08-05:00',
		file_name: '2026-02-25/birdnet/2026-02-25T073108.wav',
		classifier: 'birdnet',
	},
	{
		id: 5,
		com_name: 'White-breasted Nuthatch',
		sci_name: 'Sitta carolinensis',
		confidence: 0.55,
		date: '2026-02-25',
		time: '07:28:33',
		iso8601: '2026-02-25T07:28:33-05:00',
		file_name: '2026-02-25/birdnet/2026-02-25T072833.wav',
		classifier: 'birdnet',
	},
	{
		id: 6,
		com_name: 'Downy Woodpecker',
		sci_name: 'Dryobates pubescens',
		confidence: 0.84,
		date: '2026-02-25',
		time: '07:22:17',
		iso8601: '2026-02-25T07:22:17-05:00',
		file_name: '2026-02-25/birdnet/2026-02-25T072217.wav',
		classifier: 'birdnet',
	},
	{
		id: 7,
		com_name: 'Red-eyed Vireo',
		sci_name: 'Vireo olivaceus',
		confidence: 0.71,
		date: '2026-02-25',
		time: '07:18:44',
		iso8601: '2026-02-25T07:18:44-05:00',
		file_name: '2026-02-25/birdnet/2026-02-25T071844.wav',
		classifier: 'birdnet',
	},
	{
		id: 8,
		com_name: 'Big Brown Bat',
		sci_name: 'Eptesicus fuscus',
		confidence: 0.88,
		date: '2026-02-25',
		time: '03:42:15',
		iso8601: '2026-02-25T03:42:15-05:00',
		file_name: '2026-02-25/batdetect2/2026-02-25T034215.wav',
		classifier: 'batdetect2',
	},
	{
		id: 9,
		com_name: 'Eastern Red Bat',
		sci_name: 'Lasiurus borealis',
		confidence: 0.62,
		date: '2026-02-25',
		time: '03:38:22',
		iso8601: '2026-02-25T03:38:22-05:00',
		file_name: '2026-02-25/batdetect2/2026-02-25T033822.wav',
		classifier: 'batdetect2',
	},
	{
		id: 10,
		com_name: 'Song Sparrow',
		sci_name: 'Melospiza melodia',
		confidence: 0.95,
		date: '2026-02-25',
		time: '06:55:33',
		iso8601: '2026-02-25T06:55:33-05:00',
		file_name: '2026-02-25/birdnet/2026-02-25T065533.wav',
		classifier: 'birdnet',
	},
];

/**
 * Get mock detections, optionally filtered by date
 */
export function getMockDetections(date?: string): Detection[] {
	if (!date) return mockDetections;
	return mockDetections.filter((d) => d.date === date);
}

/**
 * Simulate a new detection arriving via SSE
 */
export function generateMockDetection(): Detection {
	const id = Date.now();
	const species = [
		{ com_name: 'Carolina Wren', sci_name: 'Thryothorus ludovicianus' },
		{ com_name: 'Tufted Titmouse', sci_name: 'Baeolophus bicolor' },
		{ com_name: 'House Finch', sci_name: 'Haemorhous mexicanus' },
		{ com_name: 'American Goldfinch', sci_name: 'Spinus tristis' },
		{ com_name: 'Dark-eyed Junco', sci_name: 'Junco hyemalis' },
	];
	const randomSpecies = species[Math.floor(Math.random() * species.length)];
	const now = new Date();
	const time = now.toTimeString().slice(0, 8);
	const date = now.toISOString().slice(0, 10);

	return {
		id,
		com_name: randomSpecies.com_name,
		sci_name: randomSpecies.sci_name,
		confidence: Math.round((Math.random() * 0.4 + 0.6) * 100) / 100,
		date,
		time,
		iso8601: now.toISOString(),
		file_name: `${date}/birdnet/${date}T${time.replace(/:/g, '')}.wav`,
		classifier: 'birdnet',
	};
}
