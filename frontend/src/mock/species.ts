import type { SpeciesSummary, SpeciesTodayResponse } from '../types';

export const mockSpecies: SpeciesSummary[] = [
  {
    com_name: 'Black-capped Chickadee',
    sci_name: 'Poecile atricapillus',
    detection_count: 12,
    max_confidence: 0.97,
    last_seen: '07:42:11',
    hourly_counts: [0, 0, 0, 0, 0, 0, 2, 3, 4, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  },
  {
    com_name: 'Northern Cardinal',
    sci_name: 'Cardinalis cardinalis',
    detection_count: 8,
    max_confidence: 0.92,
    last_seen: '08:15:33',
    hourly_counts: [0, 0, 0, 0, 0, 0, 0, 2, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  },
  {
    com_name: 'American Robin',
    sci_name: 'Turdus migratorius',
    detection_count: 6,
    max_confidence: 0.89,
    last_seen: '06:58:02',
    hourly_counts: [0, 0, 0, 0, 0, 0, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  },
  {
    com_name: 'Blue Jay',
    sci_name: 'Cyanocitta cristata',
    detection_count: 5,
    max_confidence: 0.95,
    last_seen: '09:22:47',
    hourly_counts: [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  },
  {
    com_name: 'House Finch',
    sci_name: 'Haemorhous mexicanus',
    detection_count: 4,
    max_confidence: 0.78,
    last_seen: '07:33:19',
    hourly_counts: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  },
  {
    com_name: 'Song Sparrow',
    sci_name: 'Melospiza melodia',
    detection_count: 3,
    max_confidence: 0.84,
    last_seen: '06:12:45',
    hourly_counts: [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  },
  {
    com_name: 'Tufted Titmouse',
    sci_name: 'Baeolophus bicolor',
    detection_count: 2,
    max_confidence: 0.91,
    last_seen: '08:45:03',
    hourly_counts: [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  },
  {
    com_name: 'White-breasted Nuthatch',
    sci_name: 'Sitta carolinensis',
    detection_count: 2,
    max_confidence: 0.88,
    last_seen: '07:08:56',
    hourly_counts: [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  },
];

export const mockSpeciesTodayResponse: SpeciesTodayResponse = {
  species: mockSpecies,
  generated_at: new Date().toISOString(),
};
