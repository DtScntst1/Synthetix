import { Handle, Position } from '@xyflow/react';
import { Terminal } from 'lucide-react';

export default function OutputNode({ data }: { data: any }) {
  return (
    <div className="glass-panel w-[300px] shadow-2xl border border-rose-500/30 rounded-xl overflow-hidden backdrop-blur-xl">
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-rose-400 border-2 border-black" />
      
      <div className="bg-rose-500/20 px-4 py-2 border-b border-rose-500/30 flex items-center gap-2">
        <Terminal className="w-4 h-4 text-rose-400" />
        <span className="text-xs font-bold text-rose-100 uppercase tracking-wider">Output Result</span>
      </div>
      <div className="p-4 bg-black/40 min-h-[100px] max-h-[300px] overflow-y-auto custom-scrollbar">
        {data.result ? (
          <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">{data.result}</p>
        ) : (
          <p className="text-xs text-slate-500 italic flex items-center justify-center h-full mt-6">Waiting for execution...</p>
        )}
      </div>
    </div>
  );
}
