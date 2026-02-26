/**
 * SSE Context Definition and Hook
 */

import { createContext, useContext } from 'react';
import type { ConnectionStatus } from '../types';

export interface SSEContextValue {
  connectionStatus: ConnectionStatus;
}

export const SSEContext = createContext<SSEContextValue | null>(null);

export function useSSEContext() {
  const context = useContext(SSEContext);
  if (!context) {
    throw new Error('useSSEContext must be used within SSEProvider');
  }
  return context;
}
