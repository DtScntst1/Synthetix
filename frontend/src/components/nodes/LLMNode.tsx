import { Handle, Position } from '@xyflow/react';
import { BrainCircuit } from 'lucide-react';

export default function LLMNode({ data }: { data: any }) {
  return (
    <div className="glass-panel w-[220px] shadow-2xl border border-fuchsia-500/30 rounded-xl overflow-hidden backdrop-blur-xl">
      {/* Target handle for Input/Prompt */}
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-fuchsia-400 border-2 border-black" />
      
      <div className="bg-fuchsia-500/20 px-4 py-3 flex items-center gap-2">
        <BrainCircuit className="w-5 h-5 text-fuchsia-400" />
        <div>
          <h3 className="text-sm font-bold text-fuchsia-100 uppercase tracking-wider">Groq LLM</h3>
          <p className="text-[10px] text-fuchsia-300">Llama-3.1-8b-Instant</p>
        </div>
      </div>
      
      {/* Source handle for Output */}
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-fuchsia-400 border-2 border-black" />
    </div>
  );
}
