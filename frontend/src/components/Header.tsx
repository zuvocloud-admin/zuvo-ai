import React from 'react';
import { 
  Building2, 
  Activity, 
  RefreshCw, 
  Radio, 
  ShieldCheck, 
  SmartphoneNfc,
  Sparkles,
  Database,
  Server
} from 'lucide-react';
import { TenantInfo, HealthStatus } from '../types';

interface HeaderProps {
  tenants: TenantInfo[];
  selectedTenantId: string;
  onSelectTenant: (tenantId: string) => void;
  health: HealthStatus | null;
  autoRefresh: boolean;
  onToggleAutoRefresh: () => void;
  isRefreshing: boolean;
  onManualRefresh: () => void;
  onOpenSimulation: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  tenants,
  selectedTenantId,
  onSelectTenant,
  health,
  autoRefresh,
  onToggleAutoRefresh,
  isRefreshing,
  onManualRefresh,
  onOpenSimulation,
}) => {
  const currentTenant = tenants.find((t) => t.tenant_id === selectedTenantId);

  return (
    <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40 px-4 lg:px-6 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Left: Brand & Business Title */}
        <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-start">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-emerald-600 via-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20 ring-1 ring-emerald-400/30">
              <Sparkles className="h-5 w-5 text-slate-950 font-bold" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                  ZuvoCloud
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  AI Operations
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                Store Owner Command Center & Multi-Worker WhatsApp Hub
              </p>
            </div>
          </div>

          {/* Tenant Selector Dropdown */}
          {tenants.length > 0 && (
            <div className="relative">
              <select
                value={selectedTenantId}
                onChange={(e) => onSelectTenant(e.target.value)}
                className="bg-slate-800/80 hover:bg-slate-800 text-slate-200 text-xs font-semibold rounded-lg px-3 py-1.5 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 cursor-pointer pr-8"
              >
                {tenants.map((t) => (
                  <option key={t.tenant_id} value={t.tenant_id}>
                    {t.business_name} ({t.city})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Right: Health Badges & Action Buttons */}
        <div className="flex items-center flex-wrap gap-2.5 w-full md:w-auto justify-end">
          {/* System Health Indicators */}
          <div className="hidden lg:flex items-center gap-2 bg-slate-950/60 rounded-lg p-1.5 border border-slate-800/80 text-[11px]">
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-800/60 text-slate-300">
              <Server className="h-3 w-3 text-emerald-400" />
              <span>FastAPI</span>
            </div>
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-800/60 text-slate-300">
              <Database className="h-3 w-3 text-blue-400" />
              <span>{health?.components?.database || 'Healthy'}</span>
            </div>
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-800/60 text-slate-300">
              <SmartphoneNfc className="h-3 w-3 text-whatsapp-light" />
              <span>Meta Cloud API</span>
            </div>
          </div>

          {/* Live Auto-Refresh Toggle */}
          <button
            onClick={onToggleAutoRefresh}
            className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border transition-all ${
              autoRefresh
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20'
                : 'bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700'
            }`}
            title="Toggle Live Stream Auto-Refresh (3s)"
          >
            <Radio className={`h-3.5 w-3.5 ${autoRefresh ? 'animate-pulse text-emerald-400' : 'text-slate-500'}`} />
            <span>{autoRefresh ? 'Live Stream: ON' : 'Live Stream: OFF'}</span>
          </button>

          {/* Manual Refresh Button */}
          <button
            onClick={onManualRefresh}
            disabled={isRefreshing}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition disabled:opacity-50"
            title="Refresh Feed Now"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? 'animate-spin text-emerald-400' : ''}`} />
          </button>

          {/* Inbound Simulator Launcher */}
          <button
            onClick={onOpenSimulation}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-md shadow-emerald-900/30 transition border border-emerald-400/20 active:scale-95"
          >
            <SmartphoneNfc className="h-3.5 w-3.5" />
            <span>Simulate WhatsApp</span>
          </button>
        </div>
      </div>
    </header>
  );
};
