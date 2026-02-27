/**
 * Species Chart Dialog Component
 * Displays detection distribution by date using Chart.js in a modal dialog
 */

import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import type { SpeciesDetectionHistory } from '../types';
import './SpeciesChartDialog.css';

interface SpeciesChartDialogProps {
  isOpen: boolean;
  onClose: () => void;
  species: SpeciesDetectionHistory | null;
}

export function SpeciesChartDialog({
  isOpen,
  onClose,
  species,
}: SpeciesChartDialogProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const dayOptions = [30, 180, 360, 720, 1080];

  const handleDaysChange = async (newDays: number) => {
    if (!species || !onClose) return;

    const response = await fetch(
      `/api/detections/species/history?com_name=${encodeURIComponent(species.com_name)}&days=${newDays}`
    );
    const newSpecies: SpeciesDetectionHistory = await response.json();
    onClose();

    window.dispatchEvent(
      new CustomEvent('open-chart', { detail: { species: newSpecies } })
    );
  };

  useEffect(() => {
    if (!isOpen || !species || !canvasRef.current) {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
      return;
    }

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (chartRef.current) {
      chartRef.current.destroy();
    }

    chartRef.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: species.data.map((item) => item.date),
        datasets: [
          {
            label: 'Detections',
            data: species.data.map((item) => item.count),
            backgroundColor: 'rgba(168, 198, 140, 0.12)',
            borderColor: 'rgba(168, 198, 140, 0.85)',
            borderWidth: 1.5,
            tension: 0.35,
            pointRadius: 0,
            pointHitRadius: 12,
            pointHoverRadius: 4,
            pointHoverBackgroundColor: 'rgba(168, 198, 140, 1)',
            pointHoverBorderColor: '#F0EAD2',
            pointHoverBorderWidth: 2,
          },
        ],
      },
      options: {
        layout: { padding: { right: 12, left: 4, top: 4, bottom: 4 } },
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          title: {
            display: true,
            text: `${species.com_name} — ${species.days} days`,
            color: '#E8E4D4',
            font: { size: 14, weight: 500 as const },
            padding: { bottom: 16 },
          },
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(13, 15, 11, 0.95)',
            titleColor: '#E8E4D4',
            bodyColor: '#9A9B8A',
            borderColor: '#252820',
            borderWidth: 1,
            padding: { top: 8, right: 12, bottom: 8, left: 12 },
            displayColors: false,
            titleFont: { size: 13 },
            bodyFont: { size: 12 },
          },
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(37, 40, 32, 0.5)',
            },
            ticks: {
              autoSkip: true,
              maxTicksLimit: 7,
              color: '#5A5C4E',
              font: { size: 11 },
              padding: 8,
              callback: (value: string | number) => {
                const dateStr = String(value);
                const parts = dateStr.split('-');
                if (parts.length === 3) {
                  return `${parts[1]}/${parts[2].slice(0, 2)}`;
                }
                return dateStr;
              },
            },
          },
          y: {
            min: 0,
            grid: {
              color: 'rgba(37, 40, 32, 0.3)',
            },
            ticks: {
              precision: 0,
              maxTicksLimit: 5,
              color: '#5A5C4E',
              font: { size: 11 },
              padding: 8,
            },
          },
        },
        responsive: true,
        maintainAspectRatio: false,
      },
    });

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
        chartRef.current = null;
      }
    };
  }, [isOpen, species]);

  if (!isOpen || !species) {
    return null;
  }

  return (
    <div className="chart-overlay" onClick={onClose}>
      <div
        className="chart-dialog"
        ref={containerRef}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="chart-dialog__close"
          onClick={onClose}
          aria-label="Close chart"
        >
          X
        </button>
        <div className="chart-dialog__canvas">
          <canvas ref={canvasRef} />
        </div>
        <div className="chart-dialog__controls">
          <select
            className="chart-dialog__select"
            value={species.days}
            onChange={(e) => handleDaysChange(parseInt(e.target.value))}
          >
            {dayOptions.map((days) => (
              <option key={days} value={days}>
                {days}d
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
