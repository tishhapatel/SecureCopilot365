import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, Sparkles, Mail, FileText, CheckSquare, Users, AlertTriangle } from 'lucide-react';
import { api } from '../lib/api';
import { DashboardSummaryResponse } from '../lib/types';
import RiskScoreGauge from '../components/dashboard/RiskScoreGauge';
import VendorHeatmap from '../components/dashboard/VendorHeatmap';

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.getDashboardSummary();
        setSummary(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading || !summary) {
    return (
      <div className="flex-1 flex items-center justify-center bg-darkBg text-cyberBlue">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyberBlue" />
      </div>
    );
  }

  const { risk_metrics, phishing_scans, vendor_tprm, audit_readiness, recent_threats_feed } = summary;

  return (
    <div className="flex-1 p-6 space-y-6 overflow-y-auto bg-darkBg">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-darkBorder pb-4">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
            SecureCopilot 365 CISO Hub
          </h1>
          <p className="text-xs text-gray-400 mt-1">Real-time AI Grounded Security, Compliance, & TPRM posture for Microsoft 365.</p>
        </div>
        <div className="flex items-center gap-2 bg-darkCard border border-darkBorder px-3 py-1.5 rounded-xl text-xs text-cyberBlue font-semibold shadow-glow">
          <Sparkles size={14} className="animate-pulse" /> AI Grounding Active
        </div>
      </div>

      {/* Grid: 4 Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Org Risk */}
        <div className="bg-darkCard border border-darkBorder p-4 rounded-2xl flex items-center justify-between">
          <div className="flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-gray-400">Tenant Risk Index</span>
            <span className="text-2xl font-extrabold text-white">{risk_metrics.organization_risk_score}</span>
            <span className="text-[10px] text-emerald-400 font-medium">Safe Boundary</span>
          </div>
          <div className="p-3 bg-cyberBlue/10 text-cyberBlue rounded-xl">
            <Shield size={20} />
          </div>
        </div>

        {/* Card 2: Phishing Threats */}
        <div className="bg-darkCard border border-darkBorder p-4 rounded-2xl flex items-center justify-between">
          <div className="flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-gray-400">Critical Phish Alerts</span>
            <span className="text-2xl font-extrabold text-white">{phishing_scans.critical_threats}</span>
            <span className="text-[10px] text-red-400 font-medium">Needs SOC review</span>
          </div>
          <div className="p-3 bg-red-500/10 text-red-500 rounded-xl">
            <Mail size={20} />
          </div>
        </div>

        {/* Card 3: TPRM High Risk */}
        <div className="bg-darkCard border border-darkBorder p-4 rounded-2xl flex items-center justify-between">
          <div className="flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-gray-400">TPRM Vendors Rated</span>
            <span className="text-2xl font-extrabold text-white">{vendor_tprm.total_vendors}</span>
            <span className="text-[10px] text-orange-400 font-medium">{vendor_tprm.by_tier.high} High-risk tiers</span>
          </div>
          <div className="p-3 bg-orange-500/10 text-orange-500 rounded-xl">
            <AlertTriangle size={20} />
          </div>
        </div>

        {/* Card 4: Audit readiness */}
        <div className="bg-darkCard border border-darkBorder p-4 rounded-2xl flex items-center justify-between">
          <div className="flex flex-col gap-1">
            <span className="text-[10px] uppercase font-bold text-gray-400">ISO 27001 Audit Score</span>
            <span className="text-2xl font-extrabold text-white">{audit_readiness.iso27001_readiness}%</span>
            <span className="text-[10px] text-cyberBlue font-medium">Mostly Ready band</span>
          </div>
          <div className="p-3 bg-cyberGreen/10 text-cyberGreen rounded-xl">
            <CheckSquare size={20} />
          </div>
        </div>
      </div>

      {/* Grid: 2 Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Gauges and charts (2/3 width) */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <RiskScoreGauge score={risk_metrics.organization_risk_score} label="Overall Risk Score" />
            <VendorHeatmap vendors={[]} />
          </div>

          {/* Audit status progress */}
          <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold text-sm text-gray-200">ISO 27001 Control Verification Progress</h4>
              <span className="text-xs text-cyberBlue font-semibold">{audit_readiness.controls_evidenced} / {audit_readiness.controls_total} verified</span>
            </div>
            {/* Progress bar */}
            <div className="w-full bg-darkBg h-2.5 rounded-full overflow-hidden border border-darkBorder">
              <div 
                className="bg-cyberGreen h-full rounded-full transition-all duration-1000 shadow-glow" 
                style={{ width: `${(audit_readiness.controls_evidenced / audit_readiness.controls_total) * 100}%` }}
              />
            </div>
            <div className="flex justify-between items-center text-[10px] text-gray-400">
              <span>A.5 Organizational Controls: 32/37</span>
              <span>A.8 Technological Controls: 28/34</span>
            </div>
          </div>
        </div>

        {/* Right: Threat feed & logs (1/3 width) */}
        <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 flex flex-col gap-4">
          <div className="flex items-center justify-between border-b border-darkBorder pb-2">
            <h4 className="font-semibold text-sm text-gray-200">Real-Time Threat logs</h4>
            <div className="flex items-center gap-1 text-[9px] bg-red-500/10 text-red-500 px-2 py-0.5 rounded-full font-bold uppercase">
              <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-ping" /> Live feeds
            </div>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto max-h-[360px]">
            {recent_threats_feed.map(threat => (
              <div key={threat.id} className="p-3 bg-darkBg/60 rounded-xl border border-darkBorder/40 flex flex-col gap-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-cyberBlue font-semibold uppercase">{threat.source}</span>
                  <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded ${
                    threat.risk === 'critical' ? 'text-red-400 bg-red-500/10' : 'text-orange-400 bg-orange-500/10'
                  }`}>
                    {threat.risk}
                  </span>
                </div>
                <div className="text-xs font-semibold text-gray-200">{threat.type}</div>
                <div className="flex justify-between text-[10px] text-gray-400">
                  <span>Target: {threat.target}</span>
                  <span>{threat.timestamp}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
