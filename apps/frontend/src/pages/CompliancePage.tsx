import React, { useState } from 'react';
import { FileText, Award, AlertCircle, RefreshCw, CheckSquare } from 'lucide-react';
import { api } from '../lib/api';

export default function CompliancePage() {
  const [docName, setDocName] = useState('');
  const [docText, setDocText] = useState('');
  const [frameworks, setFrameworks] = useState<string[]>(['ISO27001', 'GDPR']);
  const [checking, setChecking] = useState(false);
  const [result, setResult] = useState<any>(null);

  const toggleFramework = (fw: string) => {
    if (frameworks.includes(fw)) {
      setFrameworks(frameworks.filter(f => f !== fw));
    } else {
      setFrameworks([...frameworks, fw]);
    }
  };

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docText.trim()) return;

    setChecking(true);
    setResult(null);

    try {
      const payload = {
        document_name: docName || "Draft_Contract.txt",
        document_text: docText,
        frameworks: frameworks,
        document_type: "contract"
      };
      const res = await api.checkCompliance(payload);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setChecking(false);
    }
  };

  return (
    <div className="flex-1 p-6 space-y-6 overflow-y-auto bg-darkBg text-gray-200">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
          Regulatory Compliance Advisor
        </h1>
        <p className="text-xs text-gray-400 mt-1">Audit draft policies and third-party contracts for regulatory gaps. Generate standard remediation clauses.</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Form */}
        <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 space-y-4">
          <h3 className="font-semibold text-sm text-white flex items-center gap-2">
            <FileText size={16} className="text-cyberBlue" /> Upload Document draft
          </h3>
          <form onSubmit={handleCheck} className="space-y-4">
            <div>
              <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Document Reference Name</label>
              <input
                type="text"
                value={docName}
                onChange={e => setDocName(e.target.value)}
                placeholder="e.g. Vendor_DPA_CollaborationHub.docx"
                className="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-cyberBlue text-gray-200"
              />
            </div>
            <div>
              <label className="text-[10px] uppercase font-bold text-gray-400 block mb-2">Target Frameworks</label>
              <div className="flex flex-wrap gap-2">
                {['ISO27001', 'GDPR', 'NIST', 'HIPAA', 'SOC2'].map(fw => (
                  <button
                    key={fw}
                    type="button"
                    onClick={() => toggleFramework(fw)}
                    className={`px-3 py-1 rounded-full text-xs font-semibold border transition ${
                      frameworks.includes(fw)
                        ? 'bg-cyberBlue/10 border-cyberBlue text-cyberBlue'
                        : 'border-darkBorder bg-darkBg text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    {fw}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Document Text / Clauses</label>
              <textarea
                value={docText}
                onChange={e => setDocText(e.target.value)}
                rows={7}
                placeholder="Paste the policy paragraphs or contract clauses here for inspection..."
                className="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-cyberBlue text-gray-200"
              />
            </div>
            <button
              type="submit"
              disabled={checking}
              className="w-full bg-cyberBlue hover:bg-cyberBlue/90 text-[#0a0d16] font-bold py-2 rounded-xl text-xs transition flex items-center justify-center gap-2"
            >
              {checking ? 'Mapping Knowledge Base...' : 'Run Compliance Audit'}
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 flex flex-col gap-4">
          <h3 className="font-semibold text-sm text-white">Remediation Roadmap</h3>

          {checking && (
            <div className="flex-1 flex flex-col items-center justify-center text-cyberBlue gap-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyberBlue" />
              <span className="text-xs">Grounding document clauses...</span>
            </div>
          )}

          {!checking && !result && (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500 text-xs">
              <Award size={36} className="mb-2 text-darkBorder" />
              <span>Submit clauses to verify alignment against compliance templates.</span>
            </div>
          )}

          {!checking && result && (
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-darkBorder pb-3">
                <div>
                  <span className="text-[10px] text-gray-400 uppercase">Compliance Posture</span>
                  <div className="text-2xl font-extrabold text-white mt-0.5">{result.compliance_score} / 100</div>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-gray-400 uppercase">Frameworks Evaluated</span>
                  <div className="text-xs font-semibold text-cyberBlue mt-0.5">{result.frameworks_assessed.join(', ')}</div>
                </div>
              </div>

              {result.gaps && result.gaps.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">Compliance Gaps Found ({result.gaps.length})</h4>
                  <div className="grid gap-3 max-h-[300px] overflow-y-auto pr-1">
                    {result.gaps.map((gap: any, idx: number) => (
                      <div key={idx} className="p-3 bg-darkBg/60 rounded-xl border border-darkBorder/40 flex flex-col gap-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] text-cyberPurple font-semibold uppercase">{gap.framework} {gap.control_ref}</span>
                          <span className="text-[9px] text-red-400 font-bold uppercase">{gap.risk_level}</span>
                        </div>
                        <div className="text-xs font-semibold text-gray-200">{gap.title}</div>
                        <p className="text-[10px] text-gray-400 leading-relaxed">{gap.description}</p>
                        
                        <div className="mt-1 p-2 bg-darkBg border border-[#9d4edd]/20 rounded text-[9px] text-cyberPurple font-mono whitespace-pre-wrap leading-tight">
                          {gap.remediation}
                        </div>
                        <div className="text-[8px] text-gray-500 italic mt-0.5">Citation: {gap.citation}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.gaps && result.gaps.length === 0 && (
                <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center gap-3 text-emerald-400 text-xs font-medium">
                  <CheckSquare size={16} /> Document matches target compliance standards perfectly.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
