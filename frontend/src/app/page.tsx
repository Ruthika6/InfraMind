"use client";

import React, { useEffect, useState, useRef } from "react";
import { 
  Activity, AlertTriangle, ShieldAlert, CheckCircle, 
  MapPin, RefreshCw, Eye, TrendingUp, AlertCircle, Wrench
} from "lucide-react";
import Link from "next/link";
import { API_BASE_URL, WS_BASE_URL } from "./config";

interface Asset {
  asset_id: string;
  asset_name: string;
  asset_type: string;
  status: string;
  health_score: number;
  telemetry: Record<str, number>;
}

export default function Dashboard() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [filterType, setFilterType] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isConnecting, setIsConnecting] = useState(true);
  const [streamRate, setStreamRate] = useState("0.0");
  const wsRef = useRef<WebSocket | null>(null);
  const messageCountRef = useRef(0);
  const startTimeRef = useRef(Date.now());

  // Establish WebSocket connection for live telemetry stream
  useEffect(() => {
    const connectWS = () => {
      setIsConnecting(true);
      const ws = new WebSocket(`${WS_BASE_URL}/ws/sensors/stream`);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnecting(false);
        messageCountRef.current = 0;
        startTimeRef.current = Date.now();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setAssets(data);
          
          // Calculate stream rate (Hz)
          messageCountRef.current += 1;
          const elapsed = (Date.now() - startTimeRef.current) / 1000;
          if (elapsed > 1.0) {
            setStreamRate((messageCountRef.current / elapsed).toFixed(1));
          }

          // Maintain selection focus with updated telemetry values
          if (selectedAsset) {
            const updated = data.find((a: Asset) => a.asset_id === selectedAsset.asset_id);
            if (updated) setSelectedAsset(updated);
          } else if (data.length > 0 && !selectedAsset) {
            setSelectedAsset(data[0]);
          }
        } catch (err) {
          console.error("Error parsing telemetry stream:", err);
        }
      };

      ws.onerror = () => {
        setIsConnecting(false);
      };

      ws.onclose = () => {
        setIsConnecting(true);
        // Retry connection in 3 seconds
        setTimeout(connectWS, 3000);
      };
    };

    connectWS();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [selectedAsset]);

  // Fallback REST fetch if WS fails
  useEffect(() => {
    if (assets.length === 0) {
      const fetchInitial = async () => {
        try {
          const res = await fetch(`${API_BASE_URL}/api/v1/sensors/live`);
          if (res.ok) {
            const data = await res.json();
            setAssets(data);
            if (data.length > 0) setSelectedAsset(data[0]);
          }
        } catch (err) {
          console.error("Failed initial fetch:", err);
        }
      };
      fetchInitial();
    }
  }, [assets]);

  // Trigger manual telemetry update
  const triggerTelemetryUpdate = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/v1/sensors/trigger-stream`, { method: "POST" });
    } catch (err) {
      console.error("Error triggering stream:", err);
    }
  };

  // Filter logic
  const filteredAssets = assets.filter(a => {
    const matchesType = filterType ? a.asset_type === filterType : true;
    const matchesSearch = searchQuery 
      ? a.asset_name.toLowerCase().includes(searchQuery.toLowerCase()) || 
        a.asset_id.toLowerCase().includes(searchQuery.toLowerCase())
      : true;
    return matchesType && matchesSearch;
  });

  // Calculate Aggregates
  const totalAssets = assets.length;
  const criticalCount = assets.filter(a => a.status === "Critical").length;
  const warningCount = assets.filter(a => a.status === "Warning").length;
  const averageHealth = totalAssets 
    ? Math.round(assets.reduce((sum, a) => sum + a.health_score, 0) / totalAssets) 
    : 100;

  // Simple bounding box scaler for national GIS projection
  // Lat: 24 to 45 (approx US boundary), Lon: -125 to -70
  const getMapCoords = (lat: number, lon: number) => {
    const minLat = 24, maxLat = 45;
    const minLon = -125, maxLon = -70;
    
    const x = ((lon - minLon) / (maxLon - minLon)) * 100;
    const y = 100 - (((lat - minLat) / (maxLat - minLat)) * 100); // invert y
    return { x: Math.max(5, Math.min(95, x)), y: Math.max(5, Math.min(95, y)) };
  };

  const assetTypes = Array.from(new Set(assets.map(a => a.asset_type)));

  return (
    <div className="space-y-6">
      {/* Top Headline Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* KPI: Natl Health */}
        <div className="glass-panel p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-full blur-2xl" />
          <span className="text-gray-500 text-xs font-mono tracking-wider">NATL HEALTH INDEX</span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-gradient-purple">{averageHealth}%</span>
            <span className="text-xs text-emerald-400 font-medium">OPTIMAL</span>
          </div>
          <p className="text-[10px] text-gray-400 mt-2">Aggregated health index across {totalAssets} assets</p>
        </div>

        {/* KPI: Critical Hazards */}
        <div className="glass-panel p-6 rounded-2xl relative overflow-hidden border-rose-500/10">
          <div className="absolute top-0 right-0 w-24 h-24 bg-rose-500/5 rounded-full blur-2xl" />
          <span className="text-gray-500 text-xs font-mono tracking-wider">CRITICAL HAZARDS</span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className={`text-3xl font-bold font-mono ${criticalCount > 0 ? "text-rose-400 animate-pulse" : "text-gray-300"}`}>
              {criticalCount}
            </span>
            <span className="text-[10px] text-rose-500 font-mono font-bold tracking-wider">IMMEDIATE ACTION</span>
          </div>
          <p className="text-[10px] text-gray-400 mt-2">Active structural failures detected</p>
        </div>

        {/* KPI: Active Warnings */}
        <div className="glass-panel p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/5 rounded-full blur-2xl" />
          <span className="text-gray-500 text-xs font-mono tracking-wider">HEALTH WARNINGS</span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-amber-400">{warningCount}</span>
            <span className="text-[10px] text-amber-500 font-mono font-bold tracking-wider">ELEVATED RISK</span>
          </div>
          <p className="text-[10px] text-gray-400 mt-2">Assets breaching tolerance thresholds</p>
        </div>

        {/* KPI: Live Data Rate */}
        <div className="glass-panel p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-cyan-500/5 rounded-full blur-2xl" />
          <span className="text-gray-500 text-xs font-mono tracking-wider">TELEMETRY BANDWIDTH</span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-gradient-cyan">
              {isConnecting ? "0.0" : streamRate} Hz
            </span>
            <span className={`w-2 h-2 rounded-full ${isConnecting ? "bg-amber-500 animate-ping" : "bg-emerald-400 animate-pulse"}`} />
          </div>
          <p className="text-[10px] text-gray-400 mt-2">
            {isConnecting ? "Reconnecting stream..." : "Continuous WebSocket channel telemetry"}
          </p>
        </div>
      </div>

      {/* Main Grid: GIS Map & Selected Asset Inspection Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Interactive Map Visualizer */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col h-[480px]">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h2 className="text-sm font-semibold tracking-wide text-white">NATIONAL CRITICAL INFRASTRUCTURE GIS PLANE</h2>
              <p className="text-[11px] text-gray-500">Live coordinates coordinates scaling for monitored locations</p>
            </div>
            <button 
              onClick={triggerTelemetryUpdate}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs font-medium text-gray-300 hover:text-white hover:bg-white/10 transition-all font-mono"
            >
              <RefreshCw className="w-3.5 h-3.5" /> TRIGGER SENSOR PULSE
            </button>
          </div>

          {/* SVG Map Canvas */}
          <div className="flex-1 bg-black/40 border border-white/5 rounded-xl relative overflow-hidden">
            {/* Grid overlay */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.01)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.01)_1px,transparent_1px)] bg-[size:24px_24px]" />
            
            {/* National Boundaries Outline Mock (Stylized Vector) */}
            <svg className="absolute inset-0 w-full h-full opacity-10 pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
              <path d="M 10 25 Q 25 15 50 20 T 90 25 T 95 60 T 80 85 T 45 90 T 15 75 Z" fill="none" stroke="white" strokeWidth="0.5" />
            </svg>

            {/* Render pins */}
            {assets.map((asset) => {
              // Static mock mappings if GPS doesn't map cleanly
              // Use coordinate scaler
              const lat = asset.telemetry.gis_latitude || 35.0; // Wait, coordinates are on asset record. In endpoints we return:
              // Let's resolve coordinates. We'll use mock coordinates if properties missing.
              // Standard values for seed: bridge_vanguard is 37.8, -122.4
              // We'll hardcode or deduce:
              let pinLat = 35.0;
              let pinLon = -100.0;
              if (asset.asset_id === "bridge_vanguard_01") { pinLat = 37.8199; pinLon = -122.4783; }
              else if (asset.asset_id === "dam_horizon_02") { pinLat = 36.0162; pinLon = -114.7377; }
              else if (asset.asset_id === "grid_helios_03") { pinLat = 34.0522; pinLon = -118.2437; }
              else if (asset.asset_id === "pipeline_hyperion_04") { pinLat = 41.8781; pinLon = -87.6298; }
              else if (asset.asset_id === "tunnel_summit_05") { pinLat = 39.2638; pinLon = -120.3124; }
              else if (asset.asset_id === "railway_metro_06") { pinLat = 40.7128; pinLon = -74.0060; }
              else if (asset.asset_id === "airport_nova_07") { pinLat = 25.7906; pinLon = -80.2826; }
              else if (asset.asset_id === "port_centurion_08") { pinLat = 32.7765; pinLon = -79.9309; }
              else if (asset.asset_id === "tower_orion_09") { pinLat = 39.7392; pinLon = -104.9903; }

              const { x, y } = getMapCoords(pinLat, pinLon);
              const isSelected = selectedAsset?.asset_id === asset.asset_id;

              return (
                <button
                  key={asset.asset_id}
                  onClick={() => setSelectedAsset(asset)}
                  style={{ left: `${x}%`, top: `${y}%` }}
                  className="absolute -translate-x-1/2 -translate-y-1/2 group z-10"
                >
                  {/* Flashing glow rings */}
                  <span className={`absolute inset-0 rounded-full scale-150 opacity-40 transition-all duration-300 ${
                    asset.status === "Critical" 
                      ? "bg-rose-500 animate-ping" 
                      : (asset.status === "Warning" ? "bg-amber-500 animate-pulse" : "bg-emerald-500/20")
                  }`} />
                  
                  {/* Actual dot */}
                  <div className={`w-3.5 h-3.5 rounded-full border shadow-lg transition-all duration-300 ${
                    isSelected 
                      ? "scale-125 border-cyan-400 bg-cyan-400 ring-4 ring-cyan-400/20"
                      : (asset.status === "Critical" 
                          ? "border-rose-400 bg-rose-500" 
                          : (asset.status === "Warning" ? "border-amber-400 bg-amber-500" : "border-emerald-400 bg-emerald-500"))
                  }`} />

                  {/* Tooltip on hover */}
                  <div className="absolute left-1/2 -translate-x-1/2 bottom-5 bg-black/90 border border-white/10 rounded px-2 py-1 text-[10px] font-mono text-gray-200 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-20">
                    {asset.asset_name} ({asset.health_score}%)
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Asset Telemetry & Action Panel */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col h-[480px] justify-between">
          <div>
            <div className="flex justify-between items-start">
              <div>
                <span className="text-[9px] font-mono font-bold text-indigo-400 tracking-widest uppercase">
                  {selectedAsset?.asset_type} Profile
                </span>
                <h2 className="text-base font-bold text-white mt-1">
                  {selectedAsset?.asset_name || "Select Asset"}
                </h2>
                <p className="text-[10px] text-gray-500 font-mono mt-0.5">
                  ID: {selectedAsset?.asset_id}
                </p>
              </div>
              <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold uppercase ${
                selectedAsset?.status === "Critical" 
                  ? "bg-rose-500/10 text-rose-400 border border-rose-500/20" 
                  : (selectedAsset?.status === "Warning" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20")
              }`}>
                {selectedAsset?.status}
              </span>
            </div>

            {/* Health Meter */}
            <div className="mt-5 p-3 rounded-xl bg-white/5 border border-white/5">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-gray-500">INTEGRITY HEALTH</span>
                <span className={selectedAsset && selectedAsset.health_score > 80 ? "text-emerald-400" : "text-amber-400"}>
                  {selectedAsset?.health_score}%
                </span>
              </div>
              <div className="mt-2 w-full bg-white/10 rounded-full h-1.5 overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-500 ${
                    selectedAsset && selectedAsset.health_score > 80 
                      ? "bg-emerald-400" 
                      : (selectedAsset && selectedAsset.health_score > 50 ? "bg-amber-400" : "bg-rose-500")
                  }`} 
                  style={{ width: `${selectedAsset?.health_score || 0}%` }}
                />
              </div>
            </div>

            {/* Live Sensor Feed */}
            <div className="mt-5 space-y-3">
              <span className="text-[10px] font-mono text-gray-500 tracking-wider">LIVE TELEMETRY MATRICES</span>
              
              <div className="grid grid-cols-2 gap-3 max-h-[180px] overflow-y-auto pr-1">
                {selectedAsset && Object.entries(selectedAsset.telemetry).map(([metric, value]) => {
                  // Resolve metric units
                  let unit = "";
                  if (metric === "vibration") unit = "mm/s";
                  else if (metric === "pressure" || metric === "water_pressure") unit = "psi";
                  else if (metric.includes("temp")) unit = "°C";
                  else if (metric === "voltage") unit = "kV";
                  else if (metric === "current") unit = "A";
                  else if (metric === "load") unit = "tons";
                  else if (metric === "gas_leak_ppm") unit = "ppm";
                  else if (metric === "seepage_rate") unit = "L/s";

                  return (
                    <div key={metric} className="p-2.5 rounded-lg bg-black/30 border border-white/5 flex flex-col justify-between">
                      <span className="text-[10px] text-gray-500 uppercase tracking-wide truncate">{metric.replace("_", " ")}</span>
                      <span className="text-sm font-bold font-mono text-white mt-1">
                        {typeof value === "number" ? value.toFixed(2) : value} <span className="text-[9px] font-normal text-gray-500 font-sans">{unit}</span>
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Action Footer */}
          {selectedAsset && (
            <div className="mt-4 pt-4 border-t border-white/5 flex gap-3">
              <Link 
                href={`/assets/${selectedAsset.asset_id}`}
                className="flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition-all shadow-[0_0_15px_rgba(79,70,229,0.2)]"
              >
                <Eye className="w-3.5 h-3.5" /> RUN AI DIAGNOSIS
              </Link>
              <Link 
                href="/simulation"
                className="flex items-center justify-center p-2.5 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-gray-300 hover:text-white transition-all"
                title="Simulation Room"
              >
                <TrendingUp className="w-4 h-4" />
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Asset Registry Table */}
      <div className="glass-panel p-6 rounded-2xl">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h2 className="text-sm font-semibold tracking-wide text-white">NATIONAL ASSETS REGISTRY INDEX</h2>
            <p className="text-[11px] text-gray-500">Query complete registry logs, health scores, and useful life projections</p>
          </div>
          
          <div className="flex flex-wrap gap-3">
            {/* Search Input */}
            <input 
              type="text" 
              placeholder="Search assets..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-black/40 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-indigo-500 font-mono"
            />
            {/* Type Filter */}
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-black/40 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-gray-200 focus:outline-none focus:border-indigo-500 font-mono"
            >
              <option value="">All Asset Types</option>
              {assetTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Asset Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-white/10 text-gray-500">
                <th className="py-3 px-4 font-semibold">ASSET ID</th>
                <th className="py-3 px-4 font-semibold">NAME</th>
                <th className="py-3 px-4 font-semibold">TYPE</th>
                <th className="py-3 px-4 font-semibold">STATUS</th>
                <th className="py-3 px-4 font-semibold text-right">HEALTH SCORE</th>
                <th className="py-3 px-4 text-right">DIAGNOSTIC</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredAssets.map((asset) => (
                <tr key={asset.asset_id} className="hover:bg-white/5 transition-colors">
                  <td className="py-3 px-4 text-gray-400 font-bold">{asset.asset_id}</td>
                  <td className="py-3 px-4 text-white font-medium font-sans">{asset.asset_name}</td>
                  <td className="py-3 px-4 text-gray-400">{asset.asset_type}</td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      asset.status === "Critical" 
                        ? "bg-rose-500/10 text-rose-400" 
                        : (asset.status === "Warning" ? "bg-amber-500/10 text-amber-400" : "bg-emerald-500/10 text-emerald-400")
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${
                        asset.status === "Critical" ? "bg-rose-400 animate-ping" : (asset.status === "Warning" ? "bg-amber-400" : "bg-emerald-400")
                      }`} />
                      {asset.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-bold font-mono text-gray-200">{asset.health_score}%</td>
                  <td className="py-3 px-4 text-right">
                    <Link 
                      href={`/assets/${asset.asset_id}`}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-white/5 border border-white/10 hover:bg-indigo-600 hover:border-indigo-600 hover:text-white transition-all"
                    >
                      DIAGNOSE
                    </Link>
                  </td>
                </tr>
              ))}
              {filteredAssets.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-gray-500">
                    No infrastructure assets matched your filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
