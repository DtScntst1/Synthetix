import { Handle, Position } from '@xyflow/react';
import { MessageSquareQuote } from 'lucide-react';

export default function PromptNode({ data }: { data: any }) {
  return (
    <div className="glass-panel w-[280px] shadow-2xl border border-indigo-500/30 rounded-xl overflow-hidden backdrop-blur-xl">
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-indigo-400 border-2 border-black" />
      
      <div className="bg-indigo-500/20 px-4 py-2 border-b border-indigo-500/30 flex items-center gap-2">
        <MessageSquareQuote className="w-4 h-4 text-indigo-400" />
        <span className="text-xs font-bold text-indigo-100 uppercase tracking-wider">System Prompt</span>
      </div>
      <div className="p-4">
        <textarea 
          className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500/50 resize-none min-h-[80px]"
          placeholder="You are a helpful AI assistant..."
          defaultValue={data.value || "You are an expert assistant. Answer accurately."}
          onChange={(e) => data.onChange(e.target.value)}
        />
      </div>
      
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-indigo-400 border-2 border-black" />
    </div>
  );
}
