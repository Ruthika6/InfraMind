"use client";

import React, { useState, useEffect } from "react";
import { 
  User, Send, RefreshCw, Clipboard, FileText, CheckCircle, 
  MapPin, ShieldAlert, AlertCircle 
} from "lucide-react";
import { API_BASE_URL } from "../config";

interface CitizenReport {
  id: number;
  reporter_name: string;
  report_type: string;
  description: string;
  location: string;
  status: string;
  gemini_summary: string | null;
  created_at: string;
}

export default function CitizenPortalPage() {
  const [reports, setReports] = useState<CitizenReport[]>([]);
  const [reporterName, setReporterName] = useState("");
  const [contactInfo, setContactInfo] = useState("");
  const [reportType, setReportType] = useState("Pothole");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  
  const [isLoadingSubmit, setIsLoadingSubmit] = useState(false);
  const [isLoadingFetch, setIsLoadingFetch] = useState(false);

  const fetchReports = async () => {
    setIsLoadingFetch(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/citizen/report`);
      if (res.ok) {
        const data = await res.json();
        setReports(data);
      }
    } catch (err) {
      console.error("Failed to load citizen reports:", err);
    } finally {
      setIsLoadingFetch(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleSubmitReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!description || !location) return;
    setIsLoadingSubmit(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/citizen/report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reporter_name: reporterName || "Anonymous",
          contact_info: contactInfo || null,
          report_type: reportType,
          description: description,
          location: location,
          latitude: 37.8,
          longitude: -122.4
        })
      });
      if (res.ok) {
        // Reset form
        setReporterName("");
        setContactInfo("");
        setDescription("");
        setLocation("");
        // Reload list
        fetchReports();
      }
    } catch (err) {
      console.error("Report submission failed:", err);
    } finally {
      setIsLoadingSubmit(false);
    }
  };

  const getReportTypeColor = (type: string) => {
    const name = type.toLowerCase();
    if (name.includes("flooding") || name.includes("water")) return "bg-blue-500/10 text-blue-400 border border-blue-500/20";
    if (name.includes("gas") || name.includes("leak")) return "bg-rose-500/10 text-rose-400 border border-rose-500/20";
    if (name.includes("failure") || name.includes("power")) return "bg-amber-500/10 text-amber-400 border border-amber-500/20";
    return "bg-slate-500/10 text-slate-300 border border-slate-500/20";
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">CITIZEN PORTAL DESK</h1>
          <p className="text-xs text-gray-500 font-mono">Consolidate public incident tickets with automated AI summarize digests</p>
        </div>
        <button
          onClick={fetchReports}
          disabled={isLoadingFetch}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs font-semibold text-gray-300 hover:text-white transition-all font-mono"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoadingFetch ? "animate-spin" : ""}`} /> REFRESH INDEX
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Panel */}
        <div className="glass-panel p-6 rounded-2xl h-fit">
          <span className="text-[10px] font-mono text-gray-500 tracking-wider block mb-4">
            SUBMIT HAZARD DISCLOSURE
          </span>
          
          <form onSubmit={handleSubmitReport} className="space-y-3 font-mono text-xs">
            {/* Reporter Name */}
            <div className="space-y-1">
              <label className="text-gray-400">YOUR FULL NAME</label>
              <input 
                type="text" 
                value={reporterName} 
                onChange={(e) => setReporterName(e.target.value)}
                placeholder="Leave blank for Anonymous"
                className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Contact Info */}
            <div className="space-y-1">
              <label className="text-gray-400">CONTACT INFO (EMAIL/PHONE)</label>
              <input 
                type="text" 
                value={contactInfo} 
                onChange={(e) => setContactInfo(e.target.value)}
                placeholder="Optional contact details"
                className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Report Type */}
            <div className="space-y-1">
              <label className="text-gray-400">INCIDENT TYPE</label>
              <select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="Pothole">Pothole / Road Defect</option>
                <option value="Flooding">Flooding / Drainage Breach</option>
                <option value="Gas Leakage">Gas Leakage / Pipe Odor</option>
                <option value="Fallen Tree">Fallen Tree / Debris</option>
                <option value="Power Failure">Substation Power Failure</option>
                <option value="Bridge Photo">Bridge Structural Photo</option>
              </select>
            </div>

            {/* Location */}
            <div className="space-y-1">
              <label className="text-gray-400">LOCATION DESC</label>
              <input 
                type="text" 
                value={location} 
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Exit 18 Bridge Overpass, Lane 3"
                className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
                required
              />
            </div>

            {/* Description */}
            <div className="space-y-1">
              <label className="text-gray-400">DETAILED REPORT</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                placeholder="Describe details of the structural defect or hazard observed..."
                className="w-full bg-black/40 border border-white/10 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500 font-sans leading-relaxed"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoadingSubmit || !description || !location}
              className="w-full mt-4 flex items-center justify-center gap-2 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-700 text-white text-xs font-semibold tracking-wide transition-all shadow-[0_0_20px_rgba(99,102,241,0.2)] font-sans"
            >
              {isLoadingSubmit ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              {isLoadingSubmit ? "SUBMITTING REPORT..." : "TRANSMIT INCIDENT NOTICE"}
            </button>
          </form>
        </div>

        {/* List of Reports */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col h-[540px] justify-between">
          <div className="border-b border-white/5 pb-3">
            <span className="text-[10px] font-mono font-bold text-indigo-400 tracking-widest uppercase">
              SUBMITTED INCIDENT INDEX ({reports.length})
            </span>
          </div>

          <div className="flex-1 overflow-y-auto my-4 space-y-4 pr-1 scrollbar-hide">
            {reports.map((report) => (
              <div 
                key={report.id} 
                className="p-4 rounded-xl border border-white/5 bg-black/25 space-y-3"
              >
                <div className="flex justify-between items-start font-mono text-xs">
                  <div>
                    <span className="text-white font-bold">{report.reporter_name}</span>
                    <span className="text-gray-500 text-[10px] block">
                      Filed: {new Date(report.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${getReportTypeColor(report.report_type)}`}>
                      {report.report_type}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[9px] font-bold uppercase bg-white/5 border border-white/10 text-gray-400">
                      {report.status}
                    </span>
                  </div>
                </div>

                <div className="space-y-1 font-sans text-xs">
                  <div className="flex items-center gap-1 text-[10px] font-mono text-gray-500 uppercase">
                    <MapPin className="w-3.5 h-3.5 text-indigo-400" /> Location: {report.location}
                  </div>
                  <p className="text-gray-300 leading-relaxed font-sans">{report.description}</p>
                </div>

                {report.gemini_summary && (
                  <div className="p-3 bg-indigo-500/5 border border-indigo-500/10 rounded-lg">
                    <span className="text-[9px] font-mono font-bold text-indigo-400 tracking-wider block mb-1">
                      GEMINI COGNITIVE DIGEST
                    </span>
                    <p className="text-xs text-indigo-200/90 leading-relaxed font-sans italic">
                      "{report.gemini_summary}"
                    </p>
                  </div>
                )}
              </div>
            ))}

            {reports.length === 0 && !isLoadingFetch && (
              <div className="h-full flex flex-col justify-center items-center gap-3 py-16">
                <Clipboard className="w-12 h-12 text-gray-700" />
                <div className="text-center">
                  <h3 className="text-sm font-semibold text-gray-400">Incident Index Empty</h3>
                  <p className="text-[11px] text-gray-600 max-w-[280px] mt-1 font-mono">
                    No active citizen reports registered.
                  </p>
                </div>
              </div>
            )}
            
            {isLoadingFetch && (
              <div className="h-full flex flex-col justify-center items-center gap-3 py-16">
                <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
                <span className="text-xs text-gray-500 font-mono">Refreshing public records...</span>
              </div>
            )}
          </div>

          <div className="p-3 bg-black/30 border border-white/5 rounded-xl font-mono text-[9px] text-gray-500 flex justify-between">
            <span>PUBLIC ACCESS CHANNEL</span>
            <span>SECURED ENCRYPTION ENGINE</span>
          </div>
        </div>
      </div>
    </div>
  );
}
