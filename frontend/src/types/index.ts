/**
 * API Types for Field Station OS UI
 * Based on PRD section 7 - Backend API Contract
 */

// =============================================================================
// Detection Types
// =============================================================================

export interface Detection {
  id: number;
  com_name: string;
  sci_name: string;
  confidence: number; // 0.0-1.0
  date: string; // ISO date "2026-02-25"
  time: string; // "HH:MM:SS"
  iso8601: string; // Full ISO datetime with timezone
  file_name: string; // Relative path to .wav from audio root
  classifier: string; // "birdnet" | "batdetect2" | etc.
}

// =============================================================================
// Classifier Types
// =============================================================================

export interface ClassifierConfig {
  id: string; // "birdnet", "batdetect2", etc.
  display_name: string; // "BirdNET", "BatDetect2"
  color: string; // Hex color for badges/overlays
  enabled: boolean;
  confidence_high: number; // Threshold for green (e.g., 0.85)
  confidence_medium: number; // Threshold for amber (e.g., 0.65)
  model_name: string; // Full model identifier
  last_inference: string | null; // ISO datetime
  inference_duration_ms: number | null;
  detection_count_today: number;
}

export interface ClassifiersResponse {
  classifiers: ClassifierConfig[];
}

// =============================================================================
// Species Types
// =============================================================================

export interface SpeciesSummary {
  com_name: string;
  sci_name: string;
  detection_count: number;
  max_confidence: number;
  last_seen: string; // "HH:MM:SS"
  hourly_counts: number[]; // 24-element array, counts per hour
  is_new: boolean; // First detection was within last 2 hours
}

export interface SpeciesTodayResponse {
  species: SpeciesSummary[];
  generated_at: string; // ISO datetime
}

export interface SpeciesDetectionCount {
  date: string;
  count: number;
}

export interface SpeciesDetectionHistory {
  com_name: string;
  days: number;
  data: SpeciesDetectionCount[];
}

export interface SpeciesStats {
  com_name: string;
  sci_name: string;
  detection_count: number;
  max_confidence: number;
  best_date: string;
  best_time: string;
  best_file_name: string;
}

export interface SpeciesStatsResponse {
  species: SpeciesStats[];
  total_species: number;
  generated_at: string;
}

export interface FlickrImage {
  image_id: string;
  sci_name: string;
  com_name: string;
  image_url: string;
  title: string | null;
  author_url: string | null;
  license_url: string | null;
}

export interface FlickrImageResponse {
  sci_name: string;
  com_name: string;
  image_url: string;
  title: string | null;
  author_url: string | null;
  license_url: string | null;
  source: string;
}

export interface BlacklistRequest {
  image_id: string;
  reason?: string;
}

export interface UnblacklistRequest {
  image_id: string;
}

export interface BlacklistResponse {
  success: boolean;
  message: string;
}

// =============================================================================
// Summary Types
// =============================================================================

export interface TodaySummaryResponse {
  total_detections: number;
  species_count: number;
  top_species: Array<{ com_name: string; count: number }>;
  hourly_counts: number[]; // 24-element array
  generated_at: string;
}

// =============================================================================
// System Types
// =============================================================================

export interface SystemResponse {
  cpu_percent: number;
  temperature_celsius: number;
  temperature_fahrenheit: number;
  memory_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  uptime_seconds: number;
  active_classifiers: string[]; // Classifier IDs
  sse_subscribers: number;
  generated_at: string;
}

// =============================================================================
// Settings Types
// =============================================================================

export interface LocationWeatherResponse {
  city: string;
  temp_c: number;
  condition: string;
  latitude: number;
  longitude: number;
}

export interface SettingsResponse {
  audio_path: string;
  latitude: number;
  longitude: number;
  confidence_threshold: number;
  overlap: number;
  sensitivity: number;
  week: number;  // -1 for auto
  generated_at: string;
}

// =============================================================================
// Flickr Image Types
// =============================================================================

export interface FlickrImageResponse {
  sci_name: string;
  com_name: string;
  image_url: string;
  title: string | null;
  author_url: string | null;
  license_url: string | null;
  source: string;
}

// =============================================================================
// SSE Types
// =============================================================================

export type ConnectionStatus = 'connected' | 'reconnecting' | 'disconnected';
