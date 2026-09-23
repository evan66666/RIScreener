import type { SmartMoneySignal, SignalDetail, ScanRecord, ScanSummary } from '../types';

const BASE_URL = '/api';

export async function triggerScreening(params: {
  date_from?: string;
  date_to?: string;
  lookback_days: number;
  mode?: string;
}): Promise<{ scan_id: number; status: string; scan_mode?: string; summary: ScanSummary }> {
  const resp = await fetch(`${BASE_URL}/screen`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!resp.ok) {
    throw new Error(`Screening failed: ${resp.statusText}`);
  }
  return resp.json();
}

export async function fetchLatestScan(): Promise<{
  scan: ScanRecord | null;
  summary: ScanSummary | null;
}> {
  const resp = await fetch(`${BASE_URL}/scans/latest`);
  if (!resp.ok) {
    throw new Error('Failed to fetch latest scan');
  }
  return resp.json();
}

export async function fetchSignals(params?: {
  priority?: string;
  behavior?: string;
  action_type?: string;
  role?: string;
  stage?: string;
  impact?: string;
  ticker?: string;
  actor?: string;
  q?: string;
  date_from?: string;
  date_to?: string;
}): Promise<SmartMoneySignal[]> {
  const query = new URLSearchParams();
  if (params?.priority) query.set('priority', params.priority);
  if (params?.behavior) query.set('behavior', params.behavior);
  if (params?.action_type) query.set('action_type', params.action_type);
  if (params?.role) query.set('role', params.role);
  if (params?.stage) query.set('stage', params.stage);
  if (params?.impact) query.set('impact', params.impact);
  if (params?.ticker) query.set('ticker', params.ticker);
  if (params?.actor) query.set('actor', params.actor);
  if (params?.q) query.set('q', params.q);
  if (params?.date_from) query.set('date_from', params.date_from);
  if (params?.date_to) query.set('date_to', params.date_to);

  const url = `${BASE_URL}/signals${query.toString() ? `?${query.toString()}` : ''}`;
  const resp = await fetch(url);
  if (!resp.ok) {
    throw new Error('Failed to fetch signals');
  }
  return resp.json();
}

export async function fetchSignalDetail(id: number): Promise<SignalDetail> {
  const resp = await fetch(`${BASE_URL}/signals/${id}`);
  if (!resp.ok) {
    throw new Error('Failed to fetch signal details');
  }
  return resp.json();
}

export async function fetchActionFamilies(): Promise<{
  corporate_actions: Array<{ key: string; name: string; category: string; lifecycle_stages: any[] }>;
  corporate_transformations: Array<{ key: string; name: string }>;
}> {
  const resp = await fetch(`${BASE_URL}/action-families`);
  if (!resp.ok) {
    throw new Error('Failed to fetch action families');
  }
  return resp.json();
}
