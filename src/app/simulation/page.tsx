"use client";

import React, { useState } from "react";
import { 
  Zap, ShieldAlert, AlertTriangle, TrendingDown, 
  HelpCircle, RefreshCw, Landmark, Users, Clock, Flame
} from "lucide-react";
import { API_BASE_URL } from "../config";

interface AssetResponse {
  id: string;
  name: string;
  type: string;
  location: string;
  owner: string;
  construction_material: string;
  age_years: number;
  gis_latitude: number;
  gis_longitude: number;
  health_score: number;
  rul_months: number;
  status: string;
}

interface SimulationResponse {
  disaster_type: string;
  gis_latitude: number;
  gis_longitude: number;
  radius_km: number;
  intensity: number;
  economic_loss_millions: number;
  population_impacted: number;
  affected_assets: AssetResponse[];
  repair_cost_millions: number;
  response_timeline_days: number;
  evacuation_recommended: boolean;
  summary_report: string;
}

export default function DisasterSimulationPage() {
  const [disasterType, setDisasterType] = useState("Earthquake");
  const [lat, setLat] = useState(37.8199); // default around Vanguard Suspension Bridge
  const [lon, setLon] = useState(-122.4783);
  const [radius, setRadius] = useState(15);
  const [intensity, setIntensity] = useState(7.2);
  const [result, setResult] = useState<SimulationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const runSimulation = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/disaster/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          disaster_type: disasterType,
          gis_latitude: Number(lat),
          gis_longitude: Number(lon),
          radius_km: Number(radius),
          intensity: Number(intensity)
        })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error("Simulation run failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const getIntensityLabel = (type: string) => {
    if (type === "Earthquake") return "Richter Scale (5.0 - 9.0)";
    if (type === "Cyclone") return "Saffir-Simpson Category (1 - 5)";
    return "Severity Coef (0.1 - 1.0)";
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white tracking-wide">NATIONAL DISASTER SIMULATION SUITE</h1>
        <p className="text-xs text-gray-500 font-mono">Run physics and proximity models to forecast damage to critical grids</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Parameters panel */}
        <div className="glass-panel p-6 rounded-2xl space-y-4 h-fit">
          <span className="text-[10px] font-mono text-gray-500 tracking-wider">SIMULATION CONFIGURATOR</span>
          
          <div className="space-y-3 font-mono text-xs">
            {/* Disaster Type */}
            <div className="space-y-1">
              <label className="text-gray-400">DISASTER PHENOMENON</label>
              <select
                value={disasterType}
                onChange={(e) => {
                  setDisasterType(e.target.value);
                  if (e.target.value === "Earthquake") setIntensity(7.2);
                  else if (e.target.value === "Cyclone") setIntensity(4);
                  else setIntensity(0.8);
                }}
                className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="Earthquake">Earthquake</option>
                <option value="Cyclone">Cyclone</option>
                <option value="Dam Breach">Dam Breach</option>
                <option value="Chemical Leak">Chemical Leak</option>
                <option value="Power Outage">Power Outage</option>
                <option value="Wildfire">Wildfire</option>
              </select>
            </div>

            {/* Coordinates */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-gray-400">LATITUDE</label>
                <input 
                  type="number" 
                  step="0.0001"
                  value={lat} 
                  onChange={(e) => setLat(Number(e.target.value))}
                  className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="space-y-1">
                <label className="text-gray-400">LONGITUDE</label>
                <input 
                  type="number" 
                  step="0.0001"
                  value={lon} 
                  onChange={(e) => setLon(Number(e.target.value))}
                  className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {/* Radius */}
            <div className="space-y-1">
              <div className="flex justify-between">
                <label className="text-gray-400">DAMAGE RADIUS</label>
                <span className="text-indigo-400">{radius} km</span>
              </div>
              <input 
                type="range" 
                min="1" 
                max="50" 
                value={radius} 
                onChange={(e) => setRadius(Number(e.target.value))}
                className="w-full accent-indigo-500"
              />
            </div>

            {/* Intensity */}
            <div className="space-y-1">
              <div className="flex justify-between">
                <label className="text-gray-400 uppercase">{getIntensityLabel(disasterType)}</label>
                <span className="text-indigo-400 font-bold">{intensity}</span>
              </div>
              <input 
                type="number" 
                step="0.1"
                value={intensity} 
                onChange={(e) => setIntensity(Number(e.target.value))}
                className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <button
            onClick={runSimulation}
            disabled={isLoading}
            className="w-full mt-4 flex items-center justify-center gap-2 py-3 rounded-xl bg-rose-600 hover:bg-rose-500 disabled:bg-rose-700 text-white text-xs font-semibold tracking-wide transition-all shadow-[0_0_20px_rgba(239,68,68,0.2)]"
          >
            {isLoading ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Flame className="w-4 h-4" />
            )}
            {isLoading ? "CALCULATING SPATIAL IMPACTS..." : "RUN DISASTER SIMULATION"}
          </button>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col justify-between min-h-[420px]">
          {result ? (
            <div className="space-y-6 flex-1 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-mono font-bold text-rose-500 tracking-widest uppercase">
                    SIMULATION ASSESSMENT METRICS
                  </span>
                  
                  {result.evacuation_recommended && (
                    <span className="flex items-center gap-1 px-2.5 py-0.5 rounded text-[10px] font-bold font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20 pulse-critical">
                      <ShieldAlert className="w-3.5 h-3.5" /> EVACUATION REQUIRED
                    </span>
                  )}
                </div>

                {/* Primary KPIs */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 font-mono text-xs">
                  {/* Economic Disruption */}
                  <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                    <div className="flex items-center gap-1.5 text-gray-500">
                      <Landmark className="w-4 h-4" />
                      <span>ECONOMIC DISRUPT</span>
                    </div>
                    <p className="text-lg font-bold text-white mt-1.5">${result.economic_loss_millions}M</p>
                  </div>

                  {/* Population Impact */}
                  <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                    <div className="flex items-center gap-1.5 text-gray-500">
                      <Users className="w-4 h-4" />
                      <span>POPULATION</span>
                    </div>
                    <p className="text-lg font-bold text-white mt-1.5">{result.population_impacted.toLocaleString()}</p>
                  </div>

                  {/* Repair cost */}
                  <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                    <div className="flex items-center gap-1.5 text-gray-500">
                      <Zap className="w-4 h-4" />
                      <span>REPAIR COSTS</span>
                    </div>
                    <p className="text-lg font-bold text-rose-400 mt-1.5">${result.repair_cost_millions}M</p>
                  </div>

                  {/* Recovery Timeline */}
                  <div className="p-3 bg-black/40 border border-white/5 rounded-xl">
                    <div className="flex items-center gap-1.5 text-gray-500">
                      <Clock className="w-4 h-4" />
                      <span>RECOVERY TIME</span>
                    </div>
                    <p className="text-lg font-bold text-amber-400 mt-1.5">{result.response_timeline_days} Days</p>
                  </div>
                </div>

                {/* Summary narrative */}
                <div className="mt-6 p-4 rounded-xl bg-white/5 border border-white/5 space-y-2">
                  <span className="text-[10px] font-mono text-gray-500 tracking-wider font-bold">COGNITIVE SUMMARY REPORT</span>
                  <p className="text-xs text-gray-300 leading-relaxed font-sans">{result.summary_report}</p>
                </div>
              </div>

              {/* Affected infrastructure list */}
              <div className="mt-6">
                <span className="text-[10px] font-mono text-gray-500 tracking-wider font-bold block mb-3">
                  AFFECTED INFRASTRUCTURE ASSETS ({result.affected_assets.length})
                </span>
                
                <div className="max-h-[160px] overflow-y-auto pr-1 border border-white/5 rounded-lg bg-black/20">
                  <table className="w-full text-left text-[11px] font-mono">
                    <thead>
                      <tr className="border-b border-white/10 text-gray-500">
                        <th className="py-2 px-3">ASSET</th>
                        <th className="py-2 px-3">TYPE</th>
                        <th className="py-2 px-3 text-right">SIMULATED HEALTH</th>
                        <th className="py-2 px-3 text-right">PROJECTED STATUS</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {result.affected_assets.map(asset => (
                        <tr key={asset.id} className="hover:bg-white/5">
                          <td className="py-2 px-3 text-white">{asset.name}</td>
                          <td className="py-2 px-3 text-gray-400">{asset.type}</td>
                          <td className="py-2 px-3 text-right font-bold text-rose-400">{asset.health_score}%</td>
                          <td className="py-2 px-3 text-right">
                            <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                              {asset.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                      {result.affected_assets.length === 0 && (
                        <tr>
                          <td colSpan={4} className="py-4 text-center text-gray-500 italic">
                            No critical assets identified inside the damage perimeter.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col justify-center items-center gap-3 py-16">
              <AlertTriangle className="w-12 h-12 text-gray-700" />
              <div className="text-center">
                <h3 className="text-sm font-semibold text-gray-400">Simulation Engine Staged</h3>
                <p className="text-[11px] text-gray-600 max-w-[280px] mt-1 font-mono">
                  Input location coordinates coordinates and severity parameters to generate damage models.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
