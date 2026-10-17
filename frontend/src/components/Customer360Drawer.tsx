import React from 'react';
import { 
  Building2, 
  User, 
  Phone, 
  CreditCard, 
  IndianRupee, 
  ShieldAlert, 
  ShieldCheck, 
  Layers,
  History,
  PhoneCall
} from 'lucide-react';
import { CustomerRecord, DashboardMessageItem } from '../types';

interface Customer360DrawerProps {
  customer: CustomerRecord | null;
  messages: DashboardMessageItem[];
}

export const Customer360Drawer: React.FC<Customer360DrawerProps> = ({
  customer,
  messages,
}) => {
  if (!customer) {
    return (
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-6 flex flex-col items-center justify-center text-center h-[650px] text-slate-500 space-y-3 backdrop-blur-sm">
        <Building2 className="h-10 w-10 text-slate-700" />
        <p className="text-sm font-semibold text-slate-400">Customer 360° Profile</p>
        <p className="text-xs max-w-xs">
          Select a customer or message thread to inspect credit standing, ledger balance, and multi-worker touchpoints.
        </p>
      </div>
    );
  }

  // Calculate credit utilization
  const creditLimit = customer.credit_limit || 150000;
  const outstanding = customer.current_outstanding || 0;
  const availableCredit = Math.max(0, creditLimit - outstanding);
  const utilizationPercent = Math.min(100, Math.round((outstanding / creditLimit) * 100));

  // Determine credit status color
  const isBreached = outstanding > creditLimit;
  const isHighRisk = utilizationPercent >= 80;

  // Extract distinct workers this customer has interacted with
  const customerMessages = messages.filter(
    (m) => m.customer_id === customer.id || m.sender_phone === customer.primary_phone || m.recipient_phone === customer.primary_phone
  );

  const distinctWorkers = Array.from(
    new Set(customerMessages.map((m) => m.worker_name).filter(Boolean))
  );

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl flex flex-col h-[650px] overflow-hidden backdrop-blur-sm">
      {/* Drawer Header */}
      <div className="p-3.5 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Building2 className="h-4 w-4 text-blue-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Customer 360° View
          </span>
        </div>
        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-blue-300 border border-blue-500/20">
          Jaipur B2B Master
        </span>
      </div>

      {/* Drawer Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* 1. Profile Summary Card */}
        <div className="bg-slate-800/50 border border-slate-700/60 rounded-xl p-3.5 space-y-2.5">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-extrabold text-sm shadow-md">
              {customer.company_name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h4 className="text-sm font-bold text-white leading-tight">
                {customer.company_name}
              </h4>
              <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                <User className="h-3 w-3" />
                {customer.contact_person || 'Managing Director'}
              </p>
            </div>
          </div>

          <div className="pt-2 border-t border-slate-700/50 flex items-center justify-between text-xs font-mono text-slate-300">
            <span className="text-slate-400 flex items-center gap-1">
              <Phone className="h-3 w-3 text-emerald-400" /> Phone:
            </span>
            <span className="font-semibold">{customer.primary_phone}</span>
          </div>
        </div>

        {/* 2. Credit Standing & Ledger Risk Card */}
        <div className="bg-slate-800/50 border border-slate-700/60 rounded-xl p-3.5 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
              <CreditCard className="h-3.5 w-3.5 text-amber-400" />
              <span>Credit & Ledger Status</span>
            </span>
            {isBreached ? (
              <span className="flex items-center gap-1 text-[10px] font-extrabold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                <ShieldAlert className="h-3 w-3" /> LIMIT BREACHED
              </span>
            ) : (
              <span className="flex items-center gap-1 text-[10px] font-extrabold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                <ShieldCheck className="h-3 w-3" /> APPROVED
              </span>
            )}
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-700/50">
              <span className="text-[10px] text-slate-400 block font-medium">Approved Limit</span>
              <span className="text-sm font-bold text-white">₹{creditLimit.toLocaleString('en-IN')}</span>
            </div>
            <div className="bg-slate-900/80 p-2 rounded-lg border border-slate-700/50">
              <span className="text-[10px] text-slate-400 block font-medium">Current Outstanding</span>
              <span className={`text-sm font-bold ${isBreached ? 'text-rose-400' : 'text-amber-400'}`}>
                ₹{outstanding.toLocaleString('en-IN')}
              </span>
            </div>
          </div>

          {/* Credit Progress Bar */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-slate-400">Credit Utilization</span>
              <span className={`font-bold ${isBreached ? 'text-rose-400' : isHighRisk ? 'text-amber-400' : 'text-emerald-400'}`}>
                {utilizationPercent}% (₹{availableCredit.toLocaleString('en-IN')} free)
              </span>
            </div>
            <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden border border-slate-700/50">
              <div
                className={`h-full rounded-full transition-all ${
                  isBreached
                    ? 'bg-rose-500'
                    : isHighRisk
                    ? 'bg-amber-500'
                    : 'bg-emerald-500'
                }`}
                style={{ width: `${utilizationPercent}%` }}
              />
            </div>
          </div>
        </div>

        {/* 3. Multi-Worker Touchpoint History */}
        <div className="bg-slate-800/50 border border-slate-700/60 rounded-xl p-3.5 space-y-2.5">
          <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
            <History className="h-3.5 w-3.5 text-purple-400" />
            <span>Multi-Worker Touchpoints ({distinctWorkers.length})</span>
          </span>

          <div className="space-y-1.5">
            {distinctWorkers.length === 0 ? (
              <p className="text-[11px] text-slate-500">No interaction history recorded yet.</p>
            ) : (
              distinctWorkers.map((workerName, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between text-xs p-2 rounded-lg bg-slate-900/60 border border-slate-800"
                >
                  <div className="flex items-center gap-2">
                    <PhoneCall className="h-3 w-3 text-purple-400" />
                    <span className="font-semibold text-slate-200">{workerName}</span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">Connected</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
