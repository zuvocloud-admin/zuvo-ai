import React, { useState } from 'react';
import { Send, PhoneCall, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';
import { WhatsAppLineInfo } from '../types';

interface ReplyComposerProps {
  lines: WhatsAppLineInfo[];
  recipientPhone: string;
  onSendMessage: (payload: {
    recipient_phone: string;
    message_text: string;
    sender_number_id?: string;
  }) => Promise<void>;
}

export const ReplyComposer: React.FC<ReplyComposerProps> = ({
  lines,
  recipientPhone,
  onSendMessage,
}) => {
  const [selectedNumberId, setSelectedNumberId] = useState<string>(lines[0]?.number_id || '');
  const [targetPhone, setTargetPhone] = useState<string>(recipientPhone || '919916395385');
  const [messageText, setMessageText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Sync targetPhone when recipientPhone prop changes from left sidebar selection
  React.useEffect(() => {
    if (recipientPhone) {
      setTargetPhone(recipientPhone);
    }
  }, [recipientPhone]);

  // Sync selectedNumberId when lines are loaded
  React.useEffect(() => {
    if (lines.length > 0 && (!selectedNumberId || !lines.some((l) => l.number_id === selectedNumberId))) {
      setSelectedNumberId(lines[0].number_id);
    }
  }, [lines, selectedNumberId]);

  // Hinglish Quick Response Templates
  const templates = [
    'Namaste! Aapka order confirm kar liya hai. Dispatch kal subah hoga.',
    'Payment receive ho gaya hai. Ledger update kar diya hai. Dhanyawad!',
    'Current stock available hai. Quotation share kar rahe hain.',
    'Vehicle dispatch ho chuka hai. Driver contact details bhej rahe hain.',
  ];

  const handleSend = async () => {
    const cleanPhone = targetPhone.trim();
    if (!messageText.trim() || !cleanPhone || isSending) return;

    try {
      setIsSending(true);
      setFeedback(null);
      await onSendMessage({
        recipient_phone: cleanPhone,
        message_text: messageText.trim(),
        sender_number_id: selectedNumberId || undefined,
      });
      setMessageText('');
      setFeedback({ type: 'success', message: `WhatsApp message dispatched to ${cleanPhone} successfully!` });
      setTimeout(() => setFeedback(null), 3000);
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Failed to send message.' });
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3 backdrop-blur-sm">
      {/* Top Options Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-800 pb-2.5">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
          <Send className="h-3.5 w-3.5 text-emerald-400" />
          <span>Outbound WhatsApp Reply</span>
        </div>

        {/* Sender Line & Target Phone Selector */}
        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-slate-400 font-medium whitespace-nowrap">To:</span>
            <input
              type="text"
              value={targetPhone}
              onChange={(e) => setTargetPhone(e.target.value)}
              placeholder="e.g. 919916395385"
              className="bg-slate-950 text-slate-200 text-xs font-mono font-semibold rounded-lg px-2.5 py-1 border border-slate-700 w-32 focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
            />
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-[11px] text-slate-400 font-medium whitespace-nowrap flex items-center gap-1">
              <PhoneCall className="h-3 w-3 text-purple-400" /> From:
            </span>
            <select
              value={selectedNumberId}
              onChange={(e) => setSelectedNumberId(e.target.value)}
              className="bg-slate-800 text-slate-200 text-xs font-semibold rounded-lg px-2 py-1 border border-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 cursor-pointer"
            >
              {lines.map((l) => (
                <option key={l.number_id} value={l.number_id}>
                  {l.assigned_worker} ({l.display_phone_number})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Quick Templates Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider whitespace-nowrap">
          Quick Templates:
        </span>
        {templates.map((tpl, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => setMessageText(tpl)}
            className="text-[11px] font-medium bg-slate-800/80 hover:bg-slate-800 hover:text-emerald-300 text-slate-400 px-2.5 py-1 rounded-full border border-slate-700 whitespace-nowrap transition"
          >
            {tpl.slice(0, 30)}...
          </button>
        ))}
      </div>

      {/* Input Area */}
      <div className="relative">
        <textarea
          rows={2}
          value={messageText}
          onChange={(e) => setMessageText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Type message to ${recipientPhone || 'customer'} (Press Ctrl+Enter to send)...`}
          className="w-full bg-slate-950/80 border border-slate-700 rounded-lg p-3 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 resize-none font-sans"
        />

        <div className="absolute right-2.5 bottom-3.5 flex items-center gap-2">
          <button
            type="button"
            onClick={handleSend}
            disabled={!messageText.trim() || !targetPhone.trim() || isSending}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-md shadow-emerald-950/50 transition disabled:opacity-40 disabled:cursor-not-allowed active:scale-95"
          >
            <Send className="h-3 w-3" />
            <span>{isSending ? 'Sending...' : 'Send WhatsApp'}</span>
          </button>
        </div>
      </div>

      {/* Status Feedback */}
      {feedback && (
        <div
          className={`flex items-center gap-2 text-xs p-2 rounded-lg ${
            feedback.type === 'success'
              ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
              : 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
          }`}
        >
          {feedback.type === 'success' ? (
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
          ) : (
            <AlertCircle className="h-3.5 w-3.5 text-rose-400" />
          )}
          <span>{feedback.message}</span>
        </div>
      )}
    </div>
  );
};
