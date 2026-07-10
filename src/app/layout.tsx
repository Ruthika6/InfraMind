"use client";

import React, { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { 
  Activity, Shield, Zap, AlertTriangle, 
  Cpu, Radio, FileText, LayoutDashboard, 
  Signal, User, Bell, Clock
} from "lucide-react";
import { API_BASE_URL } from "./config";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [nationalHealth, setNationalHealth] = useState(87.5);
  const [activeAlerts, setActiveAlerts] = useState(3);
  const [currentTime, setCurrentTime] = useState("");

  useEffect(() => {
    // Local clock update
    const updateClock = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleString("en-US", { 
        hour: "numeric", 
        minute: "2-digit", 
        second: "2-digit", 
        hour12: true 
      }));
    };
    updateClock();
    const interval = setInterval(updateClock, 1000);
    
    // Fetch live dashboard metrics from the Python FastAPI backend
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/dashboard`);
        if (res.ok) {
          const data = await res.json();
          setNationalHealth(data.national_health_score);
          setActiveAlerts(data.active_alerts_count);
        }
      } catch (err) {
        // Fallback silently if backend not yet running
      }
    };
    fetchStats();
    const statsInterval = setInterval(fetchStats, 5000);

    return () => {
      clearInterval(interval);
      clearInterval(statsInterval);
    };
  }, []);

  const navItems = [
    { label: "Dashboard", href: "/", icon: LayoutDashboard },
    { label: "Disaster Room", href: "/simulation", icon: Zap },
    { label: "Agent Console", href: "/agents", icon: Cpu },
    { label: "Citizen Portal", href: "/citizen", icon: User },
  ];

  return (
    <html lang="en" className="h-full bg-[#050608] text-gray-100 antialiased">
      <body className="h-full flex overflow-hidden">
        {/* Left Sidebar Navigation */}
        <aside className="w-64 bg-[#0a0b0d] border-r border-white/5 flex flex-col justify-between shrink-0">
          <div>
            {/* Header / Logo */}
            <div className="p-6 border-b border-white/5">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
                  <Activity className="w-5 h-5 animate-pulse" />
                </div>
                <div>
                  <h1 className="font-bold text-lg tracking-wider text-white">INFRAMIND AI</h1>
                  <p className="text-[10px] text-gray-500 font-mono tracking-widest">CRITICAL INTEL</p>
                </div>
              </div>
            </div>

            {/* Menu Items */}
            <nav className="p-4 space-y-1">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive 
                        ? "bg-indigo-500/10 border-l-2 border-indigo-500 text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.1)]" 
                        : "text-gray-400 hover:text-white hover:bg-white/5"
                    }`}
                  >
                    <item.icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Bottom Diagnostics Panel */}
          <div className="p-4 border-t border-white/5 bg-black/20 font-mono text-[10px] text-gray-500 space-y-2">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5"><Signal className="w-3.5 h-3.5 text-emerald-400" /> SYSTEM STATUS</span>
              <span className="text-emerald-400">ONLINE</span>
            </div>
            <div className="flex items-center justify-between">
              <span>TELEMETRY STREAM</span>
              <span className="text-gray-300">250 HZ</span>
            </div>
            <div className="flex items-center justify-between">
              <span>ACTIVE SWARM</span>
              <span className="text-indigo-400">10 AGENTS</span>
            </div>
            <div className="mt-4 pt-3 border-t border-white/5 text-[9px] text-center text-gray-600">
              SECURE GOV COMM PORTAL
            </div>
          </div>
        </aside>

        {/* Right Content Space */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Top Header Controls */}
          <header className="h-16 bg-[#0a0b0d]/50 backdrop-blur-md border-b border-white/5 px-6 flex items-center justify-between shrink-0">
            {/* Live Indicators */}
            <div className="flex items-center gap-6">
              {/* National Score */}
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-gray-500 tracking-wider">NATL HEALTH INDEX:</span>
                <span className={`text-sm font-bold font-mono ${
                  nationalHealth > 85 ? "text-emerald-400" : (nationalHealth > 70 ? "text-amber-400" : "text-rose-400")
                }`}>
                  {nationalHealth}%
                </span>
              </div>
              <div className="h-4 w-px bg-white/10" />
              {/* Active Alerts */}
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-gray-500 tracking-wider">ACTIVE ALERTS:</span>
                <span className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                  activeAlerts > 0 ? "bg-rose-500/10 text-rose-400 border border-rose-500/20" : "bg-emerald-500/10 text-emerald-400"
                }`}>
                  <AlertTriangle className="w-3 h-3" /> {activeAlerts} CRITICAL
                </span>
              </div>
            </div>

            {/* Time / Profile Controls */}
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-gray-400 font-mono text-xs">
                <Clock className="w-3.5 h-3.5" />
                <span>{currentTime || "SYS CLOCK"}</span>
              </div>
              <div className="h-4 w-px bg-white/10" />
              <div className="flex items-center gap-3">
                <div className="relative">
                  <button className="p-1.5 rounded-lg hover:bg-white/5 text-gray-400 hover:text-white transition-colors">
                    <Bell className="w-4 h-4" />
                  </button>
                  <span className="absolute top-1 right-1 w-2 h-2 bg-rose-500 rounded-full animate-ping" />
                </div>
                <div className="flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-lg">
                  <div className="w-5 h-5 rounded-full bg-indigo-500 flex items-center justify-center text-[10px] font-bold text-white uppercase">
                    OP
                  </div>
                  <span className="text-xs font-medium text-gray-300">OP-LEAD</span>
                </div>
              </div>
            </div>
          </header>

          {/* Child Page Container */}
          <main className="flex-1 overflow-y-auto p-8 scrollbar-hide">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
