"use client";

import React, { useState, useEffect } from "react";
import { 
  Cpu, Send, RefreshCw, Layers, Shield, 
  MapPin, CheckCircle, HelpCircle, Terminal 
} from "lucide-react";
import { API_BASE_URL } from "../config";

interface AgentMessage {
  agent: string;
  message: string;
}

export default function AgentConsolePage() {
  const [assets, setAssets] = useState<any[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState("");
  const [query, setQuery] = useState("A category 4 hurricane is approaching the suspension bridge, what is our evacuation plan and drone flight status?");
  const [conversation, setConversation] = useState<AgentMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load assets to pick from
  useEffect(() => {
    const fetchAssets = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/assets`);
        if (res.ok) {
          const data = await res.json();
          setAssets(data);
          if (data.length > 0) setSelectedAssetId(data[0].id);
        }
      } catch (err) {
        console.error("Failed to load assets in agent console:", err);
      }
    };
    fetchAssets();
  }, []);

  const triggerAgentCoordination = async () => {
    if (!selectedAssetId || !query) return;
    setIsLoading(true);
    setConversation([]);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/agents?asset_id=${selectedAssetId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query })
      });
      if (res.ok) {
        const data = await res.json();
        setConversation(data.agent_conversation);
      }
    } catch (err) {
      console.error("Agent swarm execution failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const getAgentColor = (agent: string) => {
    const name = agent.toLowerCase();
    if (name.includes("supervisor")) return "border-violet-500/20 bg-violet-500/5 text-violet-400";
    if (name.includes("infrastructure")) return "border-slate-500/20 bg-slate-500/5 text-slate-300";
    if (name.includes("weather")) return "border-blue-500/20 bg-blue-500/5 text-blue-400";
    if (name.includes("emergency")) return "border-rose-500/20 bg-rose-500/5 text-rose-400";
    if (name.includes("drone")) return "border-cyan-500/20 bg-cyan-500/5 text-cyan-400";
    if (name.includes("traffic")) return "border-orange-500/20 bg-orange-500/5 text-orange-400";
    if (name.includes("finance")) return "border-amber-500/20 bg-amber-500/5 text-amber-400";
    if (name.includes("citizen")) return "border-pink-500/20 bg-pink-500/5 text-pink-400";
    if (name.includes("government")) return "border-emerald-500/20 bg-emerald-500/5 text-emerald-400";
    return "border-gray-500/20 bg-gray-500/5 text-gray-400";
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white tracking-wide">LANGGRAPH MULTI-AGENT SWARM CONSOLE</h1>
        <p className="text-xs text-gray-500 font-mono">Orchestrate specialized AI agents to evaluate hazards and draft protocols</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Swarm input panel */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 h-fit">
          <span className="text-[10px] font-mono text-gray-500 tracking-wider">SWARM COORDINATION INPUT</span>
          
          <div className="space-y-3 font-mono text-xs">
            {/* Target Asset */}
            <div className="space-y-1">
              <label className="text-gray-400">TARGET ASSET FOR ANALYSIS</label>
              <select
                value={selectedAssetId}
                onChange={(e) => setSelectedAssetId(e.target.value)}
                className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
              >
                {assets.map((asset) => (
                  <option key={asset.id} value={asset.id}>
                    {asset.name} ({asset.type})
                  </option>
                ))}
              </select>
            </div>

            {/* Swarm Prompt Query */}
            <div className="space-y-1">
              <label className="text-gray-400">COORDINATION MISSION DETAILS</label>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows={5}
                className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500 font-sans leading-relaxed"
                placeholder="Enter hazard alerts or instructions for the swarm..."
              />
            </div>
          </div>

          <button
            onClick={triggerAgentCoordination}
            disabled={isLoading || !selectedAssetId || !query}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-700 text-white text-xs font-semibold tracking-wide transition-all shadow-[0_0_20px_rgba(99,102,241,0.2)]"
          >
            {isLoading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            {isLoading ? "ROUTING STATE MACHINE..." : "INITIATE SWARM COORDINATION"}
          </button>
        </div>

        {/* Conversation Transcript Feed */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col h-[520px] justify-between">
          <div className="flex justify-between items-center border-b border-white/5 pb-3">
            <span className="text-[10px] font-mono font-bold text-indigo-400 tracking-widest uppercase">
              AGENT SWARM TRANSCRIPT DIALOGUES
            </span>
            <span className="flex items-center gap-1 text-[9px] font-mono text-gray-500">
              <Terminal className="w-3.5 h-3.5" /> LANGGRAPH ACTIVE
            </span>
          </div>

          {/* Dialogue Log */}
          <div className="flex-1 overflow-y-auto my-4 space-y-4 pr-1 scrollbar-hide">
            {conversation.map((msg, idx) => (
              <div 
                key={idx} 
                className={`p-4 rounded-xl border flex gap-3 ${getAgentColor(msg.agent)}`}
              >
                <div className="w-8 h-8 rounded-lg bg-black/40 border border-white/10 flex items-center justify-center text-xs font-bold font-mono shrink-0">
                  {msg.agent.split(" ")[0][0]}
                </div>
                <div className="space-y-1">
                  <span className="text-[10px] font-mono font-bold tracking-wider uppercase block">{msg.agent}</span>
                  <p className="text-xs leading-relaxed font-sans text-gray-200">{msg.message}</p>
                </div>
              </div>
            ))}

            {conversation.length === 0 && !isLoading && (
              <div className="h-full flex flex-col justify-center items-center gap-3 py-16">
                <Layers className="w-12 h-12 text-gray-700" />
                <div className="text-center">
                  <h3 className="text-sm font-semibold text-gray-400">Swarm Telemetry Idle</h3>
                  <p className="text-[11px] text-gray-600 max-w-[280px] mt-1 font-mono">
                    Activate swarm coordination to execute agent state steps.
                  </p>
                </div>
              </div>
            )}

            {isLoading && (
              <div className="h-full flex flex-col justify-center items-center gap-3 py-16">
                <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
                <span className="text-xs text-gray-500 font-mono">Supervisor routing graph node states...</span>
              </div>
            )}
          </div>

          {/* Status Bar */}
          <div className="p-3 bg-black/30 border border-white/5 rounded-xl font-mono text-[9px] text-gray-500 flex justify-between">
            <span>TRANSIT PROTOCOL: SIGNED</span>
            <span>GRAPH TRAVERSAL COMPLETED</span>
          </div>
        </div>
      </div>
    </div>
  );
}
