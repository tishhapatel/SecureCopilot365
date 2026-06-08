import React, { useState } from 'react';
import { Mail, Search, ShieldAlert, CheckCircle, AlertTriangle } from 'lucide-react';
import { api } from '../lib/api';

export default function PhishingPage() {
  const [subject, setSubject] = useState('');
  const [sender, setSender] = useState('');
  const [content, setContent] = useState('');
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    setScanning(true);
    setResult(null);

    try {
      const payload = {
        email_subject: subject || "Ad-Hoc Phish Scan Request",
        sender_email: sender || "external-delivery-agent@mail.com",
        sender_display: "External Courier Service",
        email_content: content,
        spf_result: "pass",
        dkim_result: "none",
        dmarc_result: "fail"
      };
      const res = await api.scanEmail(payload);
      setResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="flex-1 p-6 space-y-6 overflow-y-auto bg-darkBg text-gray-200">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
          Phishing Threat Scanner
        </h1>
        <p className="text-xs text-gray-400 mt-1">Scan email content, verify authentication headers, and map to MITRE ATT&CK. Ignore internal overrides.</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Scanner Form */}
        <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 space-y-4">
          <h3 className="font-semibold text-sm text-white flex items-center gap-2">
            <Mail size={16} className="text-cyberBlue" /> Analyze New Email
          </h3>
          <form onSubmit={handleScan} className="space-y-3">
            <div>
              <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Email Subject</label>
              <input
                type="text"
                value={subject}
                onChange={e => setSubject(e.target.value)}
                placeholder="e.g. Action Required: Update billing credentials"
                className="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-cyberBlue text-gray-200"
              />
            </div>
            <div>
              <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Sender Address</label>
              <input
                type="text"
                value={sender}
                onChange={e => setSender(e.target.value)}
                placeholder="e.g. security-microsoft@login-auth.com"
                className="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-cyberBlue text-gray-200"
              />
            </div>
            <div>
              <label className="text-[10px] uppercase font-bold text-gray-400 block mb-1">Email Content / Body</label>
              <textarea
                value={content}
                onChange={e => setContent(e.target.value)}
                rows={6}
                placeholder="Paste the email headers, body text, or links here..."
                className="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-cyberBlue text-gray-200"
              />
            </div>
            <button
              type="submit"
              disabled={scanning}
              className="w-full bg-cyberBlue hover:bg-cyberBlue/90 text-[#0a0d16] font-bold py-2 rounded-xl text-xs transition flex items-center justify-center gap-2"
            >
              {scanning ? 'Analyzing Headers...' : 'Run Phish Shield Analysis'}
            </button>
          </form>
        </div>

        {/* Results Pane */}
        <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 flex flex-col gap-4">
          <h3 className="font-semibold text-sm text-white">Detection Report</h3>
          
          {scanning && (
            <div className="flex-1 flex flex-col items-center justify-center text-cyberBlue gap-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyberBlue" />
              <span className="text-xs">SecureCopilot is executing threat metrics...</span>
            </div>
          )}

          {!scanning && !result && (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500 text-xs">
              <ShieldAlert size={36} className="mb-2 text-darkBorder" />
              <span>Input message content to trigger threat modeling.</span>
            </div>
          )}

          {!scanning && result && (
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-darkBorder pb-3">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                    result.verdict === 'safe' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                  }`}>
                    {result.verdict}
                  </span>
                  <span className="text-xs font-semibold text-gray-200">Risk Score: {result.risk_score}/100</span>
                </div>
                <div className="text-[10px] text-gray-400">Threat Band: {result.risk_level.toUpperCase()}</div>
              </div>

              <div>
                <h4 className="text-xs font-bold text-gray-400 uppercase">Analysis Summary</h4>
                <p className="text-xs mt-1 text-gray-200 leading-relaxed">{result.summary}</p>
              </div>

              {result.indicators && result.indicators.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">Threat Indicators Identified</h4>
                  <div className="grid gap-2">
                    {result.indicators.map((ind: any, idx: number) => (
                      <div key={idx} className="p-3 bg-darkBg/60 rounded-xl border border-darkBorder/40 flex items-start gap-2.5">
                        <AlertTriangle size={14} className="text-orange-400 mt-0.5" />
                        <div>
                          <div className="text-xs font-semibold text-gray-200">{ind.category}</div>
                          <div className="text-[10px] text-gray-400 mt-0.5">{ind.description}</div>
                          {ind.mitre_technique && (
                            <div className="text-[9px] text-cyberBlue font-medium mt-1">MITRE: {ind.mitre_technique}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="p-3 bg-darkBg/40 border border-darkBorder rounded-xl text-xs">
                <div className="font-semibold text-gray-300">Recommended Action:</div>
                <div className="text-gray-400 mt-1">{result.recommended_action}</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
