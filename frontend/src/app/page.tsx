"use client";

import React, { useState, useCallback, useRef } from 'react';
import { 
  ReactFlow, 
  Controls, 
  Background, 
  applyNodeChanges, 
  applyEdgeChanges, 
  NodeChange, 
  EdgeChange, 
  Node, 
  Edge,
  addEdge,
  Connection,
  ReactFlowProvider
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import Sidebar from '@/components/Sidebar';
import InputNode from '@/components/nodes/InputNode';
import PromptNode from '@/components/nodes/PromptNode';
import LLMNode from '@/components/nodes/LLMNode';
import OutputNode from '@/components/nodes/OutputNode';

// Map custom node types
const nodeTypes = {
  inputNode: InputNode,
  promptNode: PromptNode,
  llmNode: LLMNode,
  outputNode: OutputNode,
};

let id = 0;
const getId = () => `dndnode_${id++}`;

function SynthetixFlow() {
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const onNodesChange = useCallback(
    (changes: NodeChange<Node>[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );
  
  const onEdgesChange = useCallback(
    (changes: EdgeChange<Edge>[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({ ...params, animated: true, style: { stroke: '#6366f1', strokeWidth: 2 } }, eds)),
    []
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      if (typeof type === 'undefined' || !type) return;

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode: Node = {
        id: getId(),
        type,
        position,
        data: { 
          value: '', 
          onChange: (val: string) => {
            setNodes((nds) =>
              nds.map((n) => {
                if (n.id === newNode.id) return { ...n, data: { ...n.data, value: val } };
                return n;
              })
            );
          }
        },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [reactFlowInstance]
  );

  const onAddNode = useCallback((type: string) => {
    // If instance is loaded, put it in center, else fallback
    const position = reactFlowInstance 
      ? reactFlowInstance.screenToFlowPosition({ x: window.innerWidth / 2, y: window.innerHeight / 2 })
      : { x: 250, y: 250 };

    const newNode: Node = {
      id: getId(),
      type,
      position,
      data: { 
        value: '', 
        onChange: (val: string) => {
          setNodes((nds) =>
            nds.map((n) => {
              if (n.id === newNode.id) return { ...n, data: { ...n.data, value: val } };
              return n;
            })
          );
        }
      },
    };
    setNodes((nds) => nds.concat(newNode));
  }, [reactFlowInstance]);

  const executePipeline = async () => {
    setIsExecuting(true);
    
    // Clear previous outputs
    setNodes(nds => nds.map(n => {
      if (n.type === 'outputNode') return { ...n, data: { ...n.data, result: null } };
      return n;
    }));

    try {
      const payload = { nodes, edges };
      
      const response = await fetch('http://127.0.0.1:8000/api/v1/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await response.json();
      
      // Update Output Nodes with results
      setNodes(nds => nds.map(n => {
        if (n.type === 'outputNode' && data.outputs && data.outputs[n.id]) {
          return { ...n, data: { ...n.data, result: data.outputs[n.id] } };
        }
        return n;
      }));
    } catch (error) {
      console.error("Execution failed:", error);
      alert("Pipeline execution failed. Make sure Backend is running.");
    } finally {
      setIsExecuting(false);
    }
  };

  const onLoadExample = useCallback(() => {
    // Generate static IDs for the example
    const inId = getId();
    const promptId = getId();
    const llmId = getId();
    const outId = getId();

    const cx = window.innerWidth / 2;
    const cy = window.innerHeight / 2;

    const exampleNodes: Node[] = [
      {
        id: inId,
        type: 'inputNode',
        position: reactFlowInstance ? reactFlowInstance.screenToFlowPosition({ x: cx - 400, y: cy - 100 }) : { x: 100, y: 100 },
        data: { 
          value: 'Write a short poem about coding in the night.', 
          onChange: (val: string) => setNodes((nds) => nds.map((n) => (n.id === inId ? { ...n, data: { ...n.data, value: val } } : n)))
        }
      },
      {
        id: promptId,
        type: 'promptNode',
        position: reactFlowInstance ? reactFlowInstance.screenToFlowPosition({ x: cx - 400, y: cy + 100 }) : { x: 100, y: 300 },
        data: { 
          value: 'You are a poetic AI.', 
          onChange: (val: string) => setNodes((nds) => nds.map((n) => (n.id === promptId ? { ...n, data: { ...n.data, value: val } } : n)))
        }
      },
      {
        id: llmId,
        type: 'llmNode',
        position: reactFlowInstance ? reactFlowInstance.screenToFlowPosition({ x: cx, y: cy }) : { x: 450, y: 200 },
        data: {}
      },
      {
        id: outId,
        type: 'outputNode',
        position: reactFlowInstance ? reactFlowInstance.screenToFlowPosition({ x: cx + 300, y: cy }) : { x: 750, y: 200 },
        data: { result: null }
      }
    ];

    const exampleEdges: Edge[] = [
      { id: `e${inId}-${llmId}`, source: inId, target: llmId, animated: true, style: { stroke: '#6366f1', strokeWidth: 2 } },
      { id: `e${promptId}-${llmId}`, source: promptId, target: llmId, animated: true, style: { stroke: '#6366f1', strokeWidth: 2 } },
      { id: `e${llmId}-${outId}`, source: llmId, target: outId, animated: true, style: { stroke: '#6366f1', strokeWidth: 2 } }
    ];

    setNodes(exampleNodes);
    setEdges(exampleEdges);
  }, [reactFlowInstance]);

  return (
    <div className="flex h-screen w-full relative">
      <div className="bg-mesh" />
      
      <Sidebar onExecute={executePipeline} isExecuting={isExecuting} onAddNode={onAddNode} onLoadExample={onLoadExample} />
      
      <div className="flex-1 h-full relative" ref={reactFlowWrapper}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          nodeTypes={nodeTypes}
          className="bg-transparent"
        >
          <Background color="#ffffff" gap={16} size={1} opacity={0.03} />
          <Controls className="!bg-white/5 !border-white/10 !fill-white" />
        </ReactFlow>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <ReactFlowProvider>
      <SynthetixFlow />
    </ReactFlowProvider>
  );
}
