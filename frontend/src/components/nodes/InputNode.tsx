import { Handle, Position } from '@xyflow/react';
import { Type } from 'lucide-react';

export default function InputNode({ data }: { data: any }) {
  return (
    <div className="glass-panel w-[250px] shadow-2xl border border-emerald-500/30 rounded-xl overflow-hidden backdrop-blur-xl">
      <div className="bg-emerald-500/20 px-4 py-2 border-b border-emerald-500/30 flex items-center gap-2">
        <Type className="w-4 h-4 text-emerald-400" />
        <span className="text-xs font-bold text-emerald-100 uppercase tracking-wider">User Input</span>
      </div>
      <div className="p-4">
        <textarea 
          className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500/50 resize-none min-h-[60px]"
          placeholder="Enter the input text here..."
          defaultValue={data.value || "What is the capital of France?"}
          onChange={(e) => data.onChange(e.target.value)}
        />
      </div>
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-emerald-400 border-2 border-black" />
    </div>
  );
}
