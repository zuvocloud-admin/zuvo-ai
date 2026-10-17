import React, { useState } from 'react';
import { 
  X, 
  SmartphoneNfc, 
  Send, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle,
  PhoneCall,
  User,
  MessageSquare
} from 'lucide-react';
import { WhatsAppLineInfo } from '../types';

interface SimulationModalProps {
  isOpen: boolean;
  onClose: () => void;
  lines: WhatsAppLineInfo[];
  onSimulate: (payload: {
    phone_number_id: string;
    sender_phone: string;
    sender_name: string;
    message_text: string;
  }) => Promise<void>;
}

export const SimulationModal: React.FC<SimulationModalProps> = ({
  isOpen,
  onClose,
  lines,
  onSimulate,
}) => {
  if (!isOpen) return null;

  const [selectedPnId, setSelectedPnId] = useState<string>(lines[0]?.meta_phone_number_id || '1312713255253790');
  const [senderPhone, setSenderPhone] = useState('+919414099999');
  const [senderName, setSenderName] = useState('Sharma Traders (Jaipur)');
  const [messageText, setMessageText] = useState('20mm CPVC pipe ke 50 box kal subah bhej do urgent.');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  // Pre-configured B2B Distributor Scenarios
  const scenarios = [
    {
      label: '📦 CPVC Pipe Order (Hinglish)',
      customer: 'Sharma Traders (Jaipur)',
      phone: '+919414099999',
      text: '20mm CPVC pipe ke 50 box kal subah bhej do urgent.',
    },
    {
      label: '💰 RTGS Payment Update',
      customer: 'Khandelwal Sanitary Hub',
      phone: '+919414088888',
      text: 'Purane bill ka payment RTGS kar diya hai ₹1.1 Lakh.',
    },
    {
      label: '🔍 Jaguar Divertor Quote Inquiry',
      customer: 'Sharma Traders (Jaipur)',
      phone: '+919414099999',
      text: 'Suresh bhai, sample wale Jaguar divertor pasand aa gaye hain, rate bhejo.',
    },
    {
      label: '🚚 Vehicle Dispatch Logistics',
      customer: 'Rajputana Electricals & Pipes',
      phone: '+919414077777',
      text: 'Mukesh ji, vehicle RJ-14 kab tak dispatch hoga?',
    },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageText.trim() || !senderPhone.trim() || isSubmitting) return;

    try {
      setIsSubmitting(true);
      setResult(null);
      await onSimulate({
        phone_number_id: selectedPnId,
        sender_phone: senderPhone.trim(),
        sender_name: senderName.trim(),
        message_text: messageText.trim(),
      });
      setResult({ success: true, message: 'Inbound message simulated and ingested successfully!' });
      setTimeout(() => {
        onClose();
        setResult(null);
      }, 1200);
    } catch (err: any) {
      setResult({ success: false, message: err.message || 'Simulation failed.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-150">
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <SmartphoneNfc className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Inbound WhatsApp Simulator</h3>
              <p className="text-xs text-slate-400">Test Gate G6 AI routing & entity extraction</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4">
          {/* Quick Presets */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Quick B2B Trading Presets:
            </label>
            <div className="grid grid-cols-2 gap-2">
              {scenarios.map((sc, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setSenderName(sc.customer);
                    setSenderPhone(sc.phone);
                    setMessageText(sc.text);
                  }}
                  className="text-left text-xs p-2 rounded-lg bg-slate-800/80 hover:bg-slate-800 border border-slate-700/80 hover:border-emerald-500/40 text-slate-300 hover:text-emerald-300 transition"
                >
                  <span className="font-semibold block truncate">{sc.label}</span>
                  <span className="text-[10px] text-slate-500 truncate block">{sc.customer}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Receiving WhatsApp Line */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1">
              <PhoneCall className="h-3 w-3 text-purple-400" /> Target Staff WhatsApp Line:
            </label>
            <select
              value={selectedPnId}
              onChange={(e) => setSelectedPnId(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
            >
              {lines.map((l) => (
                <option key={l.meta_phone_number_id} value={l.meta_phone_number_id}>
                  {l.assigned_worker} ({l.display_phone_number}) - ID: {l.meta_phone_number_id}
                </option>
              ))}
            </select>
          </div>

          {/* Customer Name & Phone Grid */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1">
                <User className="h-3 w-3 text-blue-400" /> Party / Customer:
              </label>
              <input
                type="text"
                value={senderName}
                onChange={(e) => setSenderName(e.target.value)}
                placeholder="e.g. Sharma Traders"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1">
                <SmartphoneNfc className="h-3 w-3 text-emerald-400" /> Sender Phone:
              </label>
              <input
                type="text"
                value={senderPhone}
                onChange={(e) => setSenderPhone(e.target.value)}
                placeholder="+919414099999"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
              />
            </div>
          </div>

          {/* Inbound Message Text */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1">
              <MessageSquare className="h-3 w-3 text-teal-400" /> Inbound WhatsApp Message:
            </label>
            <textarea
              rows={3}
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              placeholder="Enter message text in Hinglish / Hindi / English..."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 resize-none font-sans"
            />
          </div>

          {/* Feedback */}
          {result && (
            <div
              className={`flex items-center gap-2 text-xs p-2.5 rounded-lg ${
                result.success
                  ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
                  : 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
              }`}
            >
              {result.success ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              ) : (
                <AlertCircle className="h-4 w-4 text-rose-400" />
              )}
              <span>{result.message}</span>
            </div>
          )}

          {/* Modal Actions */}
          <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!messageText.trim() || isSubmitting}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-950/50 transition disabled:opacity-40"
            >
              <Send className="h-3.5 w-3.5" />
              <span>{isSubmitting ? 'Simulating...' : 'Simulate Inbound Event'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
