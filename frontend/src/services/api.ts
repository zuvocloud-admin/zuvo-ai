import {
  TenantInfo,
  DashboardFeedResponse,
  CustomerRecord,
  HealthStatus,
} from '../types';

const API_BASE = '/api/v1';

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchTenants(): Promise<TenantInfo[]> {
  const res = await fetch(`${API_BASE}/dashboard/tenants`);
  if (!res.ok) throw new Error(`Failed to fetch tenants: ${res.statusText}`);
  return res.json();
}

export async function fetchCustomers(tenantId: string): Promise<CustomerRecord[]> {
  const res = await fetch(`${API_BASE}/dashboard/customers?tenant_id=${tenantId}`);
  if (!res.ok) throw new Error(`Failed to fetch customers: ${res.statusText}`);
  return res.json();
}

export async function fetchDashboardFeed(params: {
  tenantId: string;
  workerId?: string | null;
  customerId?: string | null;
  customerPhone?: string | null;
  limit?: number;
  offset?: number;
}): Promise<DashboardFeedResponse> {
  const searchParams = new URLSearchParams();
  searchParams.append('tenant_id', params.tenantId);
  if (params.workerId) searchParams.append('worker_id', params.workerId);
  if (params.customerId) searchParams.append('customer_id', params.customerId);
  if (params.customerPhone) searchParams.append('customer_phone', params.customerPhone);
  if (params.limit) searchParams.append('limit', params.limit.toString());
  if (params.offset) searchParams.append('offset', params.offset.toString());

  const res = await fetch(`${API_BASE}/dashboard/feed?${searchParams.toString()}`);
  if (!res.ok) throw new Error(`Failed to fetch feed: ${res.statusText}`);
  return res.json();
}

export async function sendOutboundMessage(payload: {
  recipient_phone: string;
  message_text: string;
  sender_number_id?: string;
}): Promise<{ status: string; wamid?: string }> {
  const res = await fetch(`${API_BASE}/messages/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    let msg = errorData.detail || `Failed to send message: ${res.statusText}`;
    if (typeof msg === 'object') msg = JSON.stringify(msg);
    if (msg.includes('Recipient phone number not in allowed list')) {
      msg = `Meta Cloud API Error: Recipient ${payload.recipient_phone} is not in your Meta Tester allowed list. Add it in Meta API Setup or test with your verified number.`;
    }
    throw new Error(msg);
  }
  return res.json();
}

export async function simulateInboundMessage(payload: {
  phone_number_id: string;
  sender_phone: string;
  sender_name: string;
  message_text: string;
}): Promise<{ status: string; wamid?: string }> {
  const res = await fetch(`${API_BASE}/messages/simulate-inbound`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    let msg = errorData.detail || `Failed to simulate message: ${res.statusText}`;
    if (typeof msg === 'object') msg = JSON.stringify(msg);
    throw new Error(msg);
  }
  return res.json();
}

