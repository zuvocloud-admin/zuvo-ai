import React from 'react';
import { MessageSquare, User, Clock, Building2 } from 'lucide-react';
import { DashboardMessageItem } from '../types';

interface ConversationsListProps {
  messages: DashboardMessageItem[];
  selectedCustomerPhone: string | null;
  onSelectCustomerPhone: (phone: string) => void;
}

export const ConversationsList: React.FC<ConversationsListProps> = ({
  messages,
  selectedCustomerPhone,
  onSelectCustomerPhone,
}) => {
  // Group messages by customer phone
  const threadMap = new Map<string, {
    customerName: string;
    customerPhone: string;
    lastMessage: DashboardMessageItem;
    count: number;
  }>();

  for (const m of messages) {
    const phone = m.customer_phone || (m.direction === 'INBOUND' ? m.sender_phone : m.recipient_phone);
    if (!threadMap.has(phone)) {
      threadMap.set(phone, {
        customerName: m.customer_name || 'Direct Contact',
        customerPhone: phone,
        lastMessage: m,
        count: 1,
      });
    } else {
      const entry = threadMap.get(phone)!;
      entry.count += 1;
    }
  }

  const threads = Array.from(threadMap.values());

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl flex flex-col h-[650px] overflow-hidden backdrop-blur-sm">
      {/* Sidebar Header */}
      <div className="p-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-emerald-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider">
            Active Threads ({threads.length})
          </span>
        </div>
      </div>

      {/* Threads List */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-800/60 p-1.5 space-y-1">
        {threads.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs">
            No active conversations matching current filters.
          </div>
        ) : (
          threads.map((t) => {
            const isSelected = selectedCustomerPhone === t.customerPhone;
            return (
              <button
                key={t.customerPhone}
                onClick={() => onSelectCustomerPhone(t.customerPhone)}
                className={`w-full text-left p-3 rounded-lg transition-all flex flex-col gap-1.5 ${
                  isSelected
                    ? 'bg-emerald-500/10 border border-emerald-500/30 text-white shadow-sm'
                    : 'hover:bg-slate-800/60 text-slate-300 border border-transparent'
                }`}
              >
                <div className="flex items-center justify-between w-full">
                  <div className="flex items-center gap-2 font-bold text-xs truncate">
                    <div className="h-6 w-6 rounded-full bg-slate-800 text-emerald-400 flex items-center justify-center text-[10px] font-extrabold ring-1 ring-slate-700">
                      {t.customerName.charAt(0).toUpperCase()}
                    </div>
                    <span className="truncate">{t.customerName}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono whitespace-nowrap">
                    {formatTime(t.lastMessage.created_at)}
                  </span>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span className="truncate max-w-[180px]">
                    {t.lastMessage.content}
                  </span>
                  <span className="px-1.5 py-0.2 rounded-full bg-slate-800 text-[10px] font-bold text-slate-300">
                    {t.count}
                  </span>
                </div>

                <div className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                  <span>{t.customerPhone}</span>
                  <span>•</span>
                  <span className="text-purple-400 truncate">
                    {t.lastMessage.worker_name}
                  </span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
};
