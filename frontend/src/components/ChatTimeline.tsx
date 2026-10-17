import React from 'react';
import { 
  CheckCheck, 
  User, 
  Sparkles, 
  PhoneCall, 
  Copy, 
  Check, 
  FileText, 
  Image as ImageIcon,
  Mic,
  Tag
} from 'lucide-react';
import { DashboardMessageItem } from '../types';

interface ChatTimelineProps {
  messages: DashboardMessageItem[];
  selectedCustomerPhone: string | null;
}

export const ChatTimeline: React.FC<ChatTimelineProps> = ({
  messages,
  selectedCustomerPhone,
}) => {
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  // Filter messages for active thread if selected, else show all in chronological order
  const displayMessages = selectedCustomerPhone
    ? messages.filter((m) => {
        const phone = m.customer_phone || (m.direction === 'INBOUND' ? m.sender_phone : m.recipient_phone);
        return phone === selectedCustomerPhone;
      })
    : messages;

  // Reverse for bottom-up chat order (oldest to newest)
  const sortedMessages = [...displayMessages].reverse();

  const activeCustomerName = sortedMessages[0]?.customer_name || 'Customer Conversation';

  const copyWamid = (wamid: string) => {
    navigator.clipboard.writeText(wamid);
    setCopiedId(wamid);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const formatTimestamp = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return isoString;
    }
  };

  const getIntentBadge = (intent: string | null) => {
    if (!intent) return null;
    switch (intent) {
      case 'CREATE_ORDER':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">📦 Order Intent</span>;
      case 'PAYMENT_COMMITMENT':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/30">💰 Payment Promise</span>;
      case 'INQUIRY_PRICE_STOCK':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">🔍 Catalog Inquiry</span>;
      case 'COMPLAINT_RETURN':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">⚠️ Complaint</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-700 text-slate-300">💬 {intent}</span>;
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl flex flex-col h-[520px] overflow-hidden backdrop-blur-sm relative">
      {/* Timeline Header */}
      <div className="px-4 py-3 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs ring-1 ring-emerald-500/30">
            {activeCustomerName.charAt(0).toUpperCase()}
          </div>
          <div>
            <h3 className="text-xs font-bold text-white flex items-center gap-2">
              <span>{activeCustomerName}</span>
              {selectedCustomerPhone && (
                <span className="text-[10px] font-mono text-slate-400 font-normal">
                  ({selectedCustomerPhone})
                </span>
              )}
            </h3>
            <p className="text-[10px] text-slate-400">
              {sortedMessages.length} interaction{sortedMessages.length !== 1 ? 's' : ''} logged in timeline
            </p>
          </div>
        </div>

        <div className="text-[11px] text-slate-400 flex items-center gap-1.5 font-medium bg-slate-800/80 px-2.5 py-1 rounded-md border border-slate-700">
          <Sparkles className="h-3 w-3 text-emerald-400" />
          <span>Real-time WhatsApp Feed</span>
        </div>
      </div>

      {/* Message Bubbles Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-950/30">
        {sortedMessages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500 space-y-2">
            <User className="h-10 w-10 text-slate-700" />
            <p className="text-sm font-semibold text-slate-400">No messages to display</p>
            <p className="text-xs max-w-sm">
              Send a test message from WhatsApp to <code className="text-emerald-400 font-mono">+1 555-675-1665</code> or use the <b className="text-slate-300">Simulate WhatsApp</b> button above.
            </p>
          </div>
        ) : (
          sortedMessages.map((m) => {
            const isInbound = m.direction === 'INBOUND';

            return (
              <div
                key={m.id}
                className={`flex flex-col ${isInbound ? 'items-start' : 'items-end'} w-full`}
              >
                {/* Bubble Container */}
                <div
                  className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-3.5 shadow-md transition-all ${
                    isInbound
                      ? 'bg-slate-800/95 border border-slate-700 text-slate-100 rounded-tl-sm'
                      : 'bg-emerald-950/80 border border-emerald-800/80 text-emerald-100 rounded-tr-sm'
                  }`}
                >
                  {/* Bubble Top Metadata Header */}
                  <div className="flex items-center justify-between gap-3 text-[10px] mb-1.5 pb-1 border-b border-slate-700/50">
                    <div className="flex items-center gap-1.5 font-semibold">
                      <span className={isInbound ? 'text-emerald-400' : 'text-teal-300'}>
                        {isInbound ? m.customer_name || m.sender_phone : 'Store Dispatch'}
                      </span>
                    </div>

                    {/* Worker Attribution Badge */}
                    <div className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-slate-900/80 text-purple-300 border border-purple-500/20 font-mono text-[9px]">
                      <PhoneCall className="h-2.5 w-2.5" />
                      <span>Line: {m.worker_name}</span>
                    </div>
                  </div>

                  {/* Message Content */}
                  <div className="text-xs leading-relaxed whitespace-pre-wrap font-sans text-slate-100">
                    {m.content}
                  </div>

                  {/* Inbound AI Entity Extraction / Intent Badge */}
                  {isInbound && m.parsed_intent && (
                    <div className="mt-2 pt-1.5 border-t border-slate-700/50 flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5">
                        {getIntentBadge(m.parsed_intent)}
                      </div>
                      {m.confidence_score !== null && (
                        <span className="text-[10px] text-slate-400 font-mono">
                          Confidence: {(m.confidence_score * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                  )}

                  {/* Bubble Footer (Time & Meta WAMID) */}
                  <div className="mt-2 flex items-center justify-between gap-2 text-[9px] text-slate-400 pt-1">
                    <button
                      onClick={() => copyWamid(m.wamid)}
                      className="font-mono hover:text-slate-200 flex items-center gap-1 text-[9px] bg-slate-900/60 px-1.5 py-0.5 rounded border border-slate-700/50 transition"
                      title="Copy Meta WhatsApp Message ID"
                    >
                      {copiedId === m.wamid ? (
                        <Check className="h-2.5 w-2.5 text-emerald-400" />
                      ) : (
                        <Copy className="h-2.5 w-2.5 text-slate-400" />
                      )}
                      <span>{m.wamid.slice(0, 14)}...</span>
                    </button>

                    <div className="flex items-center gap-1 font-mono">
                      <span>{formatTimestamp(m.created_at)}</span>
                      {!isInbound && (
                        <CheckCheck className="h-3 w-3 text-emerald-400 inline ml-0.5" />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
