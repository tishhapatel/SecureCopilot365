import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, HelpCircle, FileText, AlertTriangle } from 'lucide-react';
import { api } from '../lib/api';

export default function VendorPage() {
  const [vendorName, setVendorName] = useState('');
  const [website, setWebsite] = useState('');
  const [iso, setIso] = useState(false);
  const [soc2, setSoc2] = useState(false);
  const [dpa, setDpa] = useState(false);
  const [dataScope, setDataScope] = useState<string[]>([]);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);

  const toggleDataScope = (scope: string) => {
    if (dataScope.includes(scope)) {
      setDataScope(dataScope.filter(s => s !== scope));
    } else {
      setDataScope([...dataScope, scope]);
    }
  };

  const handleAssess = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!vendorName.trim()) return;

    setRunning(true);
    setResult(null);

    try {
      const payload = {
        vendor_name: vendorName,
        vendor_website: website || "https://vendor.io",
        data_categories: dataScope.length > 0 ? dataScope : ["personal_data_pii"],
        certifications: {
          iso27001: iso,
          soc2_type2: soc2
        },
        dpa_signed: dpa,
        questionnaire_responses: {
          mfa_enforced: true,
          encryption_configured: iso,
          logging_enabled: soc2
        },
        pen_test_date: "2025-10-01",
        sub_processors: ["Amazon Web Services"],
        incident_history: []
      };
      const res = await api.assessVendor(payload);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="flex-1 p-6 space-y-6 overflow-y-auto bg-darkBg text-gray-200">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
          Third-Party Risk Management (TPRM)
        </h1>
        <p className="text-xs text-gray-400 mt-1">Audit SaaS platform security profiles based on ISO 27001 Annex A.5.19 requirements. Generate scorecards.</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Form */}
        <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 space-y-4">
          <h3 className="font-semibold text-sm text-white flex items-center gap-2">
            <ShieldAlert size={16} className="text-cyberBlue" /> Assess Vendor Profile
          </h3>
          <form onSubmit={handleAssess} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Vendor Name</label>
                <input
                  type="text"
                  value={vendorName}
                  onChange={e => setVendorName(e.target.value)}
                  placeholder="e.g. Acme SaaS"
                  className="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-cyberBlue text-gray-200"
                  required
                />
              </div>
              <div>
                <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Website URL</label>
                <input
                  type="text"
                  value={website}
                  onChange={e => setWebsite(e.target.value)}
                  placeholder="e.g. acme-platform.io"
                  className="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-cyberBlue text-gray-200"
                />
              </div>
            </div>

            <div>
              <label className="text-[10px] uppercase font-bold text-gray-400 block mb-2">Security Certifications & Documents</label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setIso(!iso)}
                  className={`py-1.5 rounded-lg border text-xs font-semibold transition ${
                    iso ? 'bg-cyberBlue/10 border-cyberBlue text-cyberBlue' : 'border-darkBorder bg-darkBg text-gray-400'
                  }`}
                >
                  ISO 27001
                </button>
                <button
                  type="button"
                  onClick={() => setSoc2(!soc2)}
                  className={`py-1.5 rounded-lg border text-xs font-semibold transition ${
                    soc2 ? 'bg-cyberBlue/10 border-cyberBlue text-cyberBlue' : 'border-darkBorder bg-darkBg text-gray-400'
                  }`}
                >
                  SOC 2 Type II
                </button>
                <button
                  type="button"
                  onClick={() => setDpa(!dpa)}
                  className={`py-1.5 rounded-lg border text-xs font-semibold transition ${
                    dpa ? 'bg-cyberBlue/10 border-cyberBlue text-cyberBlue' : 'border-darkBorder bg-darkBg text-gray-400'
                  }`}
                >
                  DPA Signed
                </button>
              </div>
            </div>

            <div>
              <label className="text-[10px] uppercase font-bold text-gray-400 block mb-2">Processed Data Categories</label>
              <div className="flex flex-wrap gap-2">
                {['personal_data_pii', 'financial_data', 'health_data_phi', 'credentials_secrets', 'employee_data', 'public_data_only'].map(scope => (
                  <button
                    key={scope}
                    type="button"
                    onClick={() => toggleDataScope(scope)}
                    className={`px-3 py-1 rounded-full text-[10px] font-semibold border transition ${
                      dataScope.includes(scope)
                        ? 'bg-cyberBlue/10 border-cyberBlue text-cyberBlue'
                        : 'border-darkBorder bg-darkBg text-gray-400'
                    }`}
                  >
                    {scope.replace(/_/g, ' ').toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={running}
              className="w-full bg-cyberBlue hover:bg-cyberBlue/90 text-[#0a0d16] font-bold py-2 rounded-xl text-xs transition flex items-center justify-center gap-2"
            >
              {running ? 'Calculating Dimension Weights...' : 'Execute Risk Assessment'}
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 flex flex-col gap-4">
          <h3 className="font-semibold text-sm text-white font-sans">Vendor Scorecard</h3>

          {running && (
            <div className="flex-1 flex flex-col items-center justify-center text-cyberBlue gap-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyberBlue" />
              <span className="text-xs">Generating dimension weights...</span>
            </div>
          )}

          {!running && !result && (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500 text-xs">
              <HelpCircle size={36} className="mb-2 text-darkBorder" />
              <span>Input vendor compliance states to evaluate supplier risk index.</span>
            </div>
          )}

          {!running && result && (
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-darkBorder pb-3">
                <div>
                  <span className="text-[10px] text-gray-400 uppercase">Supplier Risk Tier</span>
                  <div className={`text-xl font-extrabold uppercase mt-0.5 ${
                    result.risk_tier === 'low' ? 'text-emerald-400' : 'text-orange-500'
                  }`}>{result.risk_tier}</div>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-gray-400 uppercase">Calculated Risk Index</span>
                  <div className="text-xl font-extrabold text-white mt-0.5">{result.risk_score} / 100</div>
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-gray-400 uppercase">Assessment Summary</h4>
                <p className="text-xs mt-1 text-gray-300 leading-relaxed">{result.risk_summary}</p>
              </div>

              {result.dimension_scores && (
                <div>
                  <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">TPRM Score Breakdown</h4>
                  <div className="grid grid-cols-2 gap-3">
                    {Object.entries(result.dimension_scores).map(([key, val]: any) => (
                      <div key={key} className="p-2 bg-darkBg/60 border border-darkBorder/40 rounded-xl">
                        <div className="flex justify-between items-center">
                          <span className="text-[9px] uppercase font-bold text-gray-400">{key.replace('_', ' ')}</span>
                          <span className="text-[10px] font-mono font-bold text-cyberBlue">{val.score}/100</span>
                        </div>
                        <p className="text-[9px] text-gray-500 mt-1 leading-tight">{val.details}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.findings && result.findings.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-gray-400 uppercase mb-2 font-sans">Core Architectural Findings</h4>
                  <div className="grid gap-2">
                    {result.findings.map((f: any, idx: number) => (
                      <div key={idx} className="p-3 bg-darkBg/40 border border-darkBorder/40 rounded-xl flex items-start gap-2.5">
                        <AlertTriangle size={14} className="text-red-400 mt-0.5" />
                        <div>
                          <div className="text-xs font-semibold text-gray-200">{f.finding}</div>
                          <div className="text-[10px] text-gray-400 mt-0.5">{f.recommendation}</div>
                          <div className="text-[9px] text-cyberBlue font-medium mt-1">Framework Reference: {f.citation}</div>
                        </div>
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
