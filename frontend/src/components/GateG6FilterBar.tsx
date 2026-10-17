import React from 'react';
import { 
  Users, 
  UserCheck, 
  Filter, 
  Search, 
  X, 
  Sparkles, 
  Layers,
  Phone,
  Building
} from 'lucide-react';
import { WorkerSummary, CustomerRecord } from '../types';

interface GateG6FilterBarProps {
  workers: WorkerSummary[];
  customers: CustomerRecord[];
  selectedWorkerId: string | null;
  onSelectWorker: (workerId: string | null) => void;
  selectedCustomerId: string | null;
  onSelectCustomer: (customerId: string | null) => void;
  searchPhone: string;
  onSearchPhoneChange: (phone: string) => void;
  onResetFilters: () => void;
}

export const GateG6FilterBar: React.FC<GateG6FilterBarProps> = ({
  workers,
  customers,
  selectedWorkerId,
  onSelectWorker,
  selectedCustomerId,
  onSelectCustomer,
  searchPhone,
  onSearchPhoneChange,
  onResetFilters,
}) => {
  const activeWorker = workers.find((w) => w.worker_id === selectedWorkerId);
  const activeCustomer = customers.find((c) => c.id === selectedCustomerId);
  const isFiltered = Boolean(selectedWorkerId || selectedCustomerId || searchPhone);

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-3.5 backdrop-blur-sm">
      {/* Header & Mode Explanation */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Layers className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
              <span>Gate G6 Operations Engine</span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                Multi-Worker & Customer 360°
              </span>
            </h2>
          </div>
        </div>

        {/* Reset Filter Button */}
        {isFiltered && (
          <button
            onClick={onResetFilters}
            className="flex items-center gap-1 text-xs font-semibold text-amber-400 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 px-2.5 py-1 rounded-lg border border-amber-500/30 transition"
          >
            <X className="h-3.5 w-3.5" />
            <span>Reset All Filters</span>
          </button>
        )}
      </div>

      {/* Filter Controls Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 items-center">
        {/* 1. Worker Line Segmentation (Left / lg:col-span-8) */}
        <div className="lg:col-span-7 flex items-center gap-1.5 overflow-x-auto pb-1.5 lg:pb-0 scrollbar-none">
          <span className="text-xs font-bold text-slate-400 whitespace-nowrap mr-1 flex items-center gap-1">
            <Filter className="h-3 w-3" /> Lines:
          </span>

          {/* All Workers Tab */}
          <button
            onClick={() => onSelectWorker(null)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-1.5 ${
              selectedWorkerId === null
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-900/40 ring-1 ring-emerald-400/50'
                : 'bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700/80'
            }`}
          >
            <Users className="h-3 w-3" />
            <span>All Staff Lines</span>
          </button>

          {/* Dynamic Worker Buttons */}
          {workers.map((w) => (
            <button
              key={w.worker_id}
              onClick={() => onSelectWorker(w.worker_id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all flex items-center gap-1.5 ${
                selectedWorkerId === w.worker_id
                  ? 'bg-purple-600 text-white shadow-md shadow-purple-900/40 ring-1 ring-purple-400/50'
                  : 'bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700/80'
              }`}
            >
              <UserCheck className="h-3 w-3 text-purple-300" />
              <span>{w.worker_name.split(' ')[0]}</span>
              <span className="text-[10px] text-slate-400 hidden sm:inline">
                ({w.designation.split(' ')[0]})
              </span>
            </button>
          ))}
        </div>

        {/* 2. Customer 360° Search & Dropdown (Right / lg:col-span-5) */}
        <div className="lg:col-span-5 flex items-center gap-2">
          {/* Customer Dropdown */}
          <div className="relative flex-1">
            <select
              value={selectedCustomerId || ''}
              onChange={(e) => onSelectCustomer(e.target.value || null)}
              className="w-full bg-slate-800/90 text-slate-200 text-xs font-semibold rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 cursor-pointer"
            >
              <option value="">-- Customer 360° (All Parties) --</option>
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.company_name} ({c.primary_phone})
                </option>
              ))}
            </select>
          </div>

          {/* Phone Search */}
          <div className="relative w-36">
            <input
              type="text"
              placeholder="Search phone..."
              value={searchPhone}
              onChange={(e) => onSearchPhoneChange(e.target.value)}
              className="w-full bg-slate-800/90 text-slate-200 text-xs rounded-lg pl-7 pr-2 py-2 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 placeholder:text-slate-500"
            />
            <Search className="h-3 w-3 text-slate-400 absolute left-2.5 top-2.5" />
          </div>
        </div>
      </div>

      {/* Active State Pill */}
      {isFiltered && (
        <div className="pt-2 border-t border-slate-800/60 flex items-center gap-2 text-xs">
          <span className="font-semibold text-slate-400">Active View:</span>
          {activeWorker && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20 font-medium">
              <UserCheck className="h-3 w-3" />
              Worker Line: {activeWorker.worker_name} ({activeWorker.designation})
            </span>
          )}
          {activeCustomer && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20 font-medium">
              <Building className="h-3 w-3" />
              Customer 360°: {activeCustomer.company_name} ({activeCustomer.primary_phone})
            </span>
          )}
          {searchPhone && !activeCustomer && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 font-medium">
              <Phone className="h-3 w-3" />
              Phone Match: {searchPhone}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
