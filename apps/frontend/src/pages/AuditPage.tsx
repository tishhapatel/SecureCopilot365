import React, { useState } from 'react';
import { CheckSquare, Clipboard, CloudLightning, ShieldCheck, HelpCircle } from 'lucide-react';
import { api } from '../lib/api';

export default function AuditPage() {
  const [framework, setFramework] = useState('ISO27001');
  const [evaluating, setEvaluating] = useState(false);
  const [report, setReport] = useState<any>(null);

  const handleEvaluate = async () => {
    setEvaluating(true);
    setReport(null);

    try {
      const payload = {
        framework: framework,
        collect_evidence: true,
        organization_id: "mock-tenant-id-456"
      };
      const res = await api.evaluateAudit(payload);
      setReport(res);
    } catch (err) {
      console.error(err);
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div className="flex-1 p-6 space-y-6 overflow-y-auto bg-darkBg text-gray-200">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
          Audit Readiness Center
        </h1>
        <p className="text-xs text-gray-400 mt-1">Audit active tenant configurations. Pull settings from Entra ID and SharePoint documents to verify compliance.</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left Controller */}
        <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 space-y-4 xl:col-span-1 h-fit">
          <h3 className="font-semibold text-sm text-white flex items-center gap-2">
            <Clipboard size={16} className="text-cyberBlue" /> Select Framework
          </h3>
          <div className="space-y-2">
            {['ISO27001', 'NIST', 'SOC2'].map(fw => (
              <button
                key={fw}
                onClick={() => setFramework(fw)}
                className={`w-full flex items-center justify-between p-3 rounded-xl border transition ${
                  framework === fw
                    ? 'bg-cyberBlue/10 border-cyberBlue text-cyberBlue font-bold'
                    : 'border-darkBorder bg-darkBg/60 text-gray-400 font-medium'
                }`}
              >
                <span>{fw} Framework</span>
                <span className="text-[10px] tracking-wider uppercase font-semibold">
                  {fw === 'ISO27001' ? '93 Controls' : fw === 'NIST' ? '108 Controls' : '64 Controls'}
                </span>
              </button>
            ))}
          </div>

          <button
            onClick={handleEvaluate}
            disabled={evaluating}
            className="w-full mt-2 bg-cyberBlue hover:bg-cyberBlue/90 text-[#0a0d16] font-bold py-2 rounded-xl text-xs transition flex items-center justify-center gap-2 shadow-glow"
          >
            {evaluating ? 'Running Graph Collector...' : 'Collect Evidence & Score'}
          </button>
        </div>

        {/* Right Report */}
        <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 xl:col-span-2 flex flex-col gap-4">
          <h3 className="font-semibold text-sm text-white flex items-center gap-2">
            <CloudLightning size={16} className="text-cyberGreen" /> Audit Evidence package
          </h3>

          {evaluating && (
            <div className="flex-1 flex flex-col items-center justify-center text-cyberBlue gap-2 py-10">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyberBlue" />
              <span className="text-xs">Running conditional access checkups and cataloging SharePoint policies...</span>
            </div>
          )}

          {!evaluating && !report && (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500 text-xs py-10">
              <HelpCircle size={36} className="mb-2 text-darkBorder" />
              <span>Select framework and click evaluate to gather evidence.</span>
            </div>
          )}

          {!evaluating && report && (
            <div className="space-y-5">
              <div className="grid grid-cols-4 gap-3 border-b border-darkBorder pb-4">
                <div className="bg-darkBg/60 border border-darkBorder/40 p-2.5 rounded-xl text-center">
                  <div className="text-[9px] uppercase font-bold text-gray-400">Total Controls</div>
                  <div className="text-lg font-bold text-white mt-1">{report.controls_summary.total}</div>
                </div>
                <div className="bg-darkBg/60 border border-darkBorder/40 p-2.5 rounded-xl text-center">
                  <div className="text-[9px] uppercase font-bold text-emerald-400">Sufficient</div>
                  <div className="text-lg font-bold text-emerald-400 mt-1">{report.controls_summary.evidenced}</div>
                </div>
                <div className="bg-darkBg/60 border border-darkBorder/40 p-2.5 rounded-xl text-center">
                  <div className="text-[9px] uppercase font-bold text-yellow-400">Partial</div>
                  <div className="text-lg font-bold text-yellow-400 mt-1">{report.controls_summary.partial}</div>
                </div>
                <div className="bg-darkBg/60 border border-darkBorder/40 p-2.5 rounded-xl text-center">
                  <div className="text-[9px] uppercase font-bold text-red-400">Missing</div>
                  <div className="text-lg font-bold text-red-400 mt-1">{report.controls_summary.missing}</div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-gray-400 uppercase">Executive Summary</h4>
                <p className="text-xs mt-1.5 text-gray-300 leading-relaxed bg-darkBg/30 p-3 rounded-xl border border-darkBorder/40">{report.executive_summary}</p>
              </div>

              {report.critical_gaps && report.critical_gaps.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">Major Gaps flag</h4>
                  <div className="grid gap-2">
                    {report.critical_gaps.map((gap: any, idx: number) => (
                      <div key={idx} className="p-3 bg-darkBg/60 rounded-xl border border-red-500/20 flex flex-col gap-1.5">
                        <div className="flex justify-between items-center text-[10px]">
                          <span className="font-semibold text-cyberPurple">{gap.control_ref} — {gap.control_name}</span>
                          <span className="text-red-400 font-bold uppercase">Days to fix: {gap.days_to_remediate}</span>
                        </div>
                        <p className="text-[10px] text-gray-300 mt-0.5">{gap.gap_description}</p>
                        <div className="text-[9px] text-cyberGreen font-semibold mt-1">Needed Evidence: {gap.evidence_needed}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {report.collected_evidence && report.collected_evidence.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">Evidence packages validated</h4>
                  <div className="grid gap-2">
                    {report.collected_evidence.map((ev: any, idx: number) => (
                      <div key={idx} className="p-2.5 bg-darkBg/40 border border-darkBorder/40 rounded-xl flex items-center justify-between">
                        <div className="flex flex-col">
                          <span className="text-xs font-semibold text-gray-200">{ev.evidence_type}</span>
                          <span className="text-[9px] text-gray-500 mt-0.5">Source: {ev.source}</span>
                        </div>
                        <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded-full ${
                          ev.status === 'sufficient' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-yellow-500/10 text-yellow-400'
                        }`}>
                          {ev.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
