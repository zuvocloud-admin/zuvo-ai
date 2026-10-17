import React from 'react';
import { 
  MessageSquareText, 
  Users, 
  PhoneCall, 
  IndianRupee, 
  ArrowDownLeft, 
  ArrowUpRight 
} from 'lucide-react';
import { DashboardMetrics, CustomerRecord } from '../types';

interface MetricsCardsProps {
  metrics: DashboardMetrics | null;
  customers: CustomerRecord[];
}

export const MetricsCards: React.FC<MetricsCardsProps> = ({ metrics, customers }) => {
  // Calculate total outstanding across all customers
  const totalOutstanding = customers.reduce((sum, c) => sum + (c.current_outstanding || 0), 0);
  const totalCreditLimit = customers.reduce((sum, c) => sum + (c.credit_limit || 0), 0);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Total Messages Today */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 relative overflow-hidden backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Total Messages Today
          </span>
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <MessageSquareText className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-extrabold text-white tracking-tight">
            {metrics?.total_messages_today ?? 0}
          </span>
          <span className="text-xs text-slate-400 font-medium">events</span>
        </div>
        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center gap-3 text-[11px]">
          <span className="flex items-center gap-1 text-emerald-400 font-medium">
            <ArrowDownLeft className="h-3 w-3" /> In: {metrics?.total_inbound ?? 0}
          </span>
          <span className="text-slate-600">|</span>
          <span className="flex items-center gap-1 text-blue-400 font-medium">
            <ArrowUpRight className="h-3 w-3" /> Out: {metrics?.total_outbound ?? 0}
          </span>
        </div>
      </div>

      {/* 2. Active Wholesale Customers */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 relative overflow-hidden backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Active B2B Accounts
          </span>
          <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Users className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-extrabold text-white tracking-tight">
            {customers.length || metrics?.active_customers_count || 0}
          </span>
          <span className="text-xs text-slate-400 font-medium">parties</span>
        </div>
        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
          <span>Customer 360° Profiles</span>
          <span className="text-emerald-400 font-semibold">100% Tracked</span>
        </div>
      </div>

      {/* 3. Connected Staff Lines */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 relative overflow-hidden backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            WhatsApp Staff Lines
          </span>
          <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <PhoneCall className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-extrabold text-white tracking-tight">
            {metrics?.active_workers_count ?? 5}
          </span>
          <span className="text-xs text-slate-400 font-medium">active lines</span>
        </div>
        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
          <span>Gate G6 Isolation</span>
          <span className="text-purple-400 font-semibold">Attributed</span>
        </div>
      </div>

      {/* 4. Total Outstanding Credit Ledger */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 relative overflow-hidden backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Total Ledger Outstanding
          </span>
          <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <IndianRupee className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-2 flex items-baseline gap-2">
          <span className="text-2xl font-extrabold text-amber-400 tracking-tight">
            ₹{(totalOutstanding / 100000).toFixed(2)} L
          </span>
          <span className="text-xs text-slate-400 font-medium">
            (of ₹{(totalCreditLimit / 100000).toFixed(1)} L limit)
          </span>
        </div>
        <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
          <span>Deterministic Guardrail</span>
          <span className="text-amber-400 font-semibold">Active</span>
        </div>
      </div>
    </div>
  );
};
