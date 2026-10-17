import React, { useState, useEffect, useCallback } from 'react';
import { 
  fetchHealth, 
  fetchTenants, 
  fetchCustomers, 
  fetchDashboardFeed, 
  sendOutboundMessage, 
  simulateInboundMessage 
} from './services/api';
import { 
  TenantInfo, 
  HealthStatus, 
  DashboardFeedResponse, 
  CustomerRecord, 
  DashboardMessageItem 
} from './types';
import { Header } from './components/Header';
import { MetricsCards } from './components/MetricsCards';
import { GateG6FilterBar } from './components/GateG6FilterBar';
import { ConversationsList } from './components/ConversationsList';
import { ChatTimeline } from './components/ChatTimeline';
import { ReplyComposer } from './components/ReplyComposer';
import { Customer360Drawer } from './components/Customer360Drawer';
import { SimulationModal } from './components/SimulationModal';

export const App: React.FC = () => {
  // Global State
  const [tenants, setTenants] = useState<TenantInfo[]>([]);
  const [selectedTenantId, setSelectedTenantId] = useState<string>('');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [customers, setCustomers] = useState<CustomerRecord[]>([]);
  const [feedData, setFeedData] = useState<DashboardFeedResponse | null>(null);
  
  // Gate G6 Filter State
  const [selectedWorkerId, setSelectedWorkerId] = useState<string | null>(null);
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  const [searchPhone, setSearchPhone] = useState<string>('');
  
  // Active Thread / Customer Selection in UI
  const [activeCustomerPhone, setActiveCustomerPhone] = useState<string | null>(null);

  // Auto-Refresh & UI State
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [isSimulationOpen, setIsSimulationOpen] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // 1. Initial Load: Tenants & Health
  useEffect(() => {
    const init = async () => {
      try {
        const [healthRes, tenantsRes] = await Promise.all([
          fetchHealth().catch(() => null),
          fetchTenants(),
        ]);
        setHealth(healthRes);
        setTenants(tenantsRes);
        if (tenantsRes.length > 0 && !selectedTenantId) {
          setSelectedTenantId(tenantsRes[0].tenant_id);
        }
      } catch (err: any) {
        setError(err.message || 'Failed to initialize ZuvoCloud platform.');
      }
    };
    init();
  }, []);

  // 2. Load Customers when Tenant changes
  useEffect(() => {
    if (!selectedTenantId) return;
    fetchCustomers(selectedTenantId)
      .then(setCustomers)
      .catch((err) => console.error('Failed to load customers:', err));
  }, [selectedTenantId]);

  // 3. Load Feed Data with Gate G6 Filters
  const loadFeed = useCallback(async (showSpinner = false) => {
    if (!selectedTenantId) return;
    if (showSpinner) setIsRefreshing(true);

    try {
      const data = await fetchDashboardFeed({
        tenantId: selectedTenantId,
        workerId: selectedWorkerId,
        customerId: selectedCustomerId,
        customerPhone: searchPhone || undefined,
        limit: 100,
      });
      setFeedData(data);
      setError(null);

      // Default active thread to first customer if none selected
      if (!activeCustomerPhone && data.messages.length > 0) {
        const firstPhone = data.messages[0].customer_phone || data.messages[0].sender_phone;
        setActiveCustomerPhone(firstPhone);
      }
    } catch (err: any) {
      console.error('Feed fetch error:', err);
    } finally {
      if (showSpinner) setIsRefreshing(false);
    }
  }, [selectedTenantId, selectedWorkerId, selectedCustomerId, searchPhone, activeCustomerPhone]);

  // 4. Trigger Feed Load on Filter Changes
  useEffect(() => {
    loadFeed(true);
  }, [loadFeed]);

  // 5. Polling Engine (every 3 seconds when autoRefresh is enabled)
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      loadFeed(false);
    }, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh, loadFeed]);

  // Handler: Customer Selection from Filter Dropdown
  const handleSelectCustomerFilter = (customerId: string | null) => {
    setSelectedCustomerId(customerId);
    if (customerId) {
      const cust = customers.find((c) => c.id === customerId);
      if (cust) setActiveCustomerPhone(cust.primary_phone);
    }
  };

  // Handler: Reset Filters
  const handleResetFilters = () => {
    setSelectedWorkerId(null);
    setSelectedCustomerId(null);
    setSearchPhone('');
  };

  // Handler: Send Outbound WhatsApp Reply
  const handleSendOutbound = async (payload: {
    recipient_phone: string;
    message_text: string;
    sender_number_id?: string;
  }) => {
    await sendOutboundMessage(payload);
    await loadFeed(false);
  };

  // Handler: Simulate Inbound Event
  const handleSimulate = async (payload: {
    phone_number_id: string;
    sender_phone: string;
    sender_name: string;
    message_text: string;
  }) => {
    await simulateInboundMessage(payload);
    await loadFeed(false);
  };

  // Determine current active customer profile for the 360° drawer
  const currentCustomer = customers.find(
    (c) => c.primary_phone === activeCustomerPhone || c.id === selectedCustomerId
  ) || null;

  const currentTenant = tenants.find((t) => t.tenant_id === selectedTenantId);
  const activeLines = currentTenant?.whatsapp_lines || [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-emerald-500 selection:text-slate-950">
      {/* Top Navbar */}
      <Header
        tenants={tenants}
        selectedTenantId={selectedTenantId}
        onSelectTenant={(id) => {
          setSelectedTenantId(id);
          handleResetFilters();
          setActiveCustomerPhone(null);
        }}
        health={health}
        autoRefresh={autoRefresh}
        onToggleAutoRefresh={() => setAutoRefresh(!autoRefresh)}
        isRefreshing={isRefreshing}
        onManualRefresh={() => loadFeed(true)}
        onOpenSimulation={() => setIsSimulationOpen(true)}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto w-full px-4 lg:px-6 py-6 space-y-5 flex-1">
        {/* Error Banner if any */}
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 p-3 rounded-xl text-xs font-semibold">
            {error}
          </div>
        )}

        {/* 1. Metrics & Business Pulse Row */}
        <MetricsCards
          metrics={feedData?.metrics || null}
          customers={customers}
        />

        {/* 2. Gate G6 Multi-Worker Line & Customer 360° Filter Bar */}
        <GateG6FilterBar
          workers={feedData?.workers || []}
          customers={customers}
          selectedWorkerId={selectedWorkerId}
          onSelectWorker={setSelectedWorkerId}
          selectedCustomerId={selectedCustomerId}
          onSelectCustomer={handleSelectCustomerFilter}
          searchPhone={searchPhone}
          onSearchPhoneChange={setSearchPhone}
          onResetFilters={handleResetFilters}
        />

        {/* 3. Three-Column Workspace Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Left Column: Active Threads List (3 cols) */}
          <div className="lg:col-span-3">
            <ConversationsList
              messages={feedData?.messages || []}
              selectedCustomerPhone={activeCustomerPhone}
              onSelectCustomerPhone={(phone) => {
                setActiveCustomerPhone(phone);
                // Sync customer filter if matching
                const matched = customers.find((c) => c.primary_phone === phone);
                if (matched) setSelectedCustomerId(matched.id);
              }}
            />
          </div>

          {/* Center Column: WhatsApp Chat Timeline & Outbound Composer (6 cols) */}
          <div className="lg:col-span-6 space-y-3">
            <ChatTimeline
              messages={feedData?.messages || []}
              selectedCustomerPhone={activeCustomerPhone}
            />

            {/* Outbound WhatsApp Reply Composer */}
            <ReplyComposer
              lines={activeLines}
              recipientPhone={activeCustomerPhone || ''}
              onSendMessage={handleSendOutbound}
            />
          </div>

          {/* Right Column: Customer 360° & Credit Ledger Details (3 cols) */}
          <div className="lg:col-span-3">
            <Customer360Drawer
              customer={currentCustomer}
              messages={feedData?.messages || []}
            />
          </div>
        </div>
      </main>

      {/* Inbound WhatsApp Simulator Modal */}
      <SimulationModal
        isOpen={isSimulationOpen}
        onClose={() => setIsSimulationOpen(false)}
        lines={activeLines}
        onSimulate={handleSimulate}
      />
    </div>
  );
};
