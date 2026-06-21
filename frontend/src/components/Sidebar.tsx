import React from 'react';
import { Type, MessageSquareQuote, BrainCircuit, Terminal, Play, Loader2 } from 'lucide-react';

interface SidebarProps {
  onExecute: () => void;
  isExecuting: boolean;
  onAddNode: (type: string) => void;
  onLoadExample: () => void;
}

export default function Sidebar({ onExecute, isExecuting, onAddNode, onLoadExample }: SidebarProps) {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside className="w-64 h-full glass-panel border-r border-white/10 flex flex-col z-10 shadow-2xl relative">
      <div className="p-6 border-b border-white/5">
        <h1 className="text-xl font-bold text-gradient tracking-tight mb-1">Synthetix</h1>
        <p className="text-xs text-slate-400">Visual AI Pipeline Orchestrator</p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">Node Palette</h2>
        
        <div className="space-y-3">
          <div 
            className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl cursor-pointer hover:bg-emerald-500/20 transition-colors flex items-center gap-3"
            onDragStart={(event) => onDragStart(event, 'inputNode')}
            onClick={() => onAddNode('inputNode')}
            draggable
          >
            <div className="bg-emerald-500/20 p-2 rounded-lg"><Type className="w-4 h-4 text-emerald-400" /></div>
            <span className="text-sm font-medium text-emerald-100">User Input</span>
          </div>

          <div 
            className="p-3 bg-indigo-500/10 border border-indigo-500/30 rounded-xl cursor-pointer hover:bg-indigo-500/20 transition-colors flex items-center gap-3"
            onDragStart={(event) => onDragStart(event, 'promptNode')}
            onClick={() => onAddNode('promptNode')}
            draggable
          >
            <div className="bg-indigo-500/20 p-2 rounded-lg"><MessageSquareQuote className="w-4 h-4 text-indigo-400" /></div>
            <span className="text-sm font-medium text-indigo-100">System Prompt</span>
          </div>

          <div 
            className="p-3 bg-fuchsia-500/10 border border-fuchsia-500/30 rounded-xl cursor-pointer hover:bg-fuchsia-500/20 transition-colors flex items-center gap-3"
            onDragStart={(event) => onDragStart(event, 'llmNode')}
            onClick={() => onAddNode('llmNode')}
            draggable
          >
            <div className="bg-fuchsia-500/20 p-2 rounded-lg"><BrainCircuit className="w-4 h-4 text-fuchsia-400" /></div>
            <span className="text-sm font-medium text-fuchsia-100">Groq LLM</span>
          </div>

          <div 
            className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl cursor-pointer hover:bg-rose-500/20 transition-colors flex items-center gap-3"
            onDragStart={(event) => onDragStart(event, 'outputNode')}
            onClick={() => onAddNode('outputNode')}
            draggable
          >
            <div className="bg-rose-500/20 p-2 rounded-lg"><Terminal className="w-4 h-4 text-rose-400" /></div>
            <span className="text-sm font-medium text-rose-100">Output Result</span>
          </div>
        </div>
        
        <div className="mt-6 border-t border-white/5 pt-4">
          <button 
            onClick={onLoadExample}
            className="w-full py-2 bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 rounded-lg text-xs font-semibold transition-colors"
          >
            ✨ Load Example Template
          </button>
        </div>
      </div>

      <div className="p-4 border-t border-white/5 bg-black/20">
        <button 
          onClick={onExecute}
          disabled={isExecuting}
          className="w-full py-3 bg-gradient-to-r from-indigo-500 to-fuchsia-500 hover:from-indigo-400 hover:to-fuchsia-400 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg disabled:opacity-50"
        >
          {isExecuting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Play className="w-5 h-5 fill-current" />}
          {isExecuting ? 'Executing...' : 'Run Pipeline'}
        </button>
      </div>
    </aside>
  );
}
