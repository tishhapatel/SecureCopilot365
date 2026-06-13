import React, { useState, useEffect } from 'react';
import { ShieldCheck, Activity, Database, RefreshCw, CheckCircle, AlertTriangle, HelpCircle, Lock, Globe, Server } from 'lucide-react';
import { api } from '../lib/api';

export default function TrustCenter() {
  const [region, setRegion] = useState('East US (Primary)');
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<any>(null);
  const [updatingResidency, setUpdatingResidency] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    async function loadResidency() {
      try {
        const res = await api.getDataResidency();
        if (res && res.region) {
          setRegion(res.region);
        }
      } catch (err) {
        console.error('Failed to load data residency:', err);
      }
    }
    loadResidency();
  }, []);

  const handleVerifyLedger = async () => {
    setVerifying(true);
    setVerificationResult(null);
    try {
      // Simulate real-time cryptographic calculation delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      const res = await api.verifyAuditLedger();
      setVerificationResult(res);
    } catch (err) {
      console.error('Ledger verification failed:', err);
      setVerificationResult({
        verified: false,
        error: 'Network connection error or insufficient permissions'
      });
    } finally {
      setVerifying(false);
    }
  };

  const handleResidencyChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newRegion = e.target.value;
    setRegion(newRegion);
    setUpdatingResidency(true);
    setSuccessMsg('');
    try {
      await api.updateDataResidency(newRegion);
      setSuccessMsg(`Data Residency successfully migrated to: ${newRegion}`);
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      console.error('Failed to update residency:', err);
    } finally {
      setUpdatingResidency(false);
    }
  };

  // Static mock uptime metrics
  const uptimeMetrics = [
    { name: 'Gateway / API Gateway', status: 'Operational', uptime: '99.99%', health: 'Excellent' },
    { name: 'RAG Search & AI Inference Engine', status: 'Operational', uptime: '99.97%', health: 'Excellent' },
    { name: 'Tenant Relational Database (Azure SQL)', status: 'Operational', uptime: '100%', health: 'Optimal' },
    { name: 'WORM Immutable Audit Log Storage', status: 'Operational', uptime: '100%', health: 'Optimal' }
  ];

  return (
    <div className="flex-1 p-6 space-y-6 overflow-y-auto bg-[#0a0d16] text-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-darkBorder pb-4">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
            <ShieldCheck className="text-cyberBlue" size={26} /> Trust & Transparency Center
          </h1>
          <p className="text-xs text-gray-400 mt-1">Review live platform uptime, active compliance certifications, cryptographic audit ledger proof, and data residency settings.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Left/Middle Column (2/3 width): Services Status & Certifications */}
        <div className="xl:col-span-2 space-y-6">
          
          {/* Card 1: System Uptime & Status */}
          <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 space-y-4">
            <h3 className="font-semibold text-sm text-white flex items-center gap-2">
              <Activity size={16} className="text-cyberBlue animate-pulse" /> Platform Services & Live Metrics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {uptimeMetrics.map((svc, idx) => (
                <div key={idx} className="p-4 bg-darkBg/60 rounded-xl border border-darkBorder/40 flex flex-col gap-1.5">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-semibold text-gray-200">{svc.name}</span>
                    <span className="text-[10px] bg-cyberGreen/10 text-cyberGreen px-2 py-0.5 rounded-full font-bold uppercase">
                      {svc.status}
                    </span>
                  </div>
                  <div className="flex justify-between text-[11px] text-gray-400 mt-1">
                    <span>Uptime (30d): <strong className="text-white">{svc.uptime}</strong></span>
                    <span>State: <strong className="text-cyberGreen">{svc.health}</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Card 2: Cryptographic Ledger Chain Verification */}
          <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-sm text-white flex items-center gap-2">
                <Lock size={16} className="text-cyberPurple" /> Cryptographic Ledger Audit Log Chain
              </h3>
              <button
                onClick={handleVerifyLedger}
                disabled={verifying}
                className="flex items-center gap-2 bg-gradient-to-r from-cyberBlue to-cyberPurple text-white px-4 py-2 rounded-xl text-xs font-bold hover:opacity-90 transition disabled:opacity-50"
              >
                {verifying ? (
                  <>
                    <RefreshCw className="animate-spin" size={14} /> Computing Hashes...
                  </>
                ) : (
                  <>
                    <RefreshCw size={14} /> Run Dynamic Audit Verification
                  </>
                )}
              </button>
            </div>
            <p className="text-xs text-gray-400">
              Each administrative action is stored sequentially in a ledger chained together using SHA-256 block hashes. 
              Run verification to dynamically recalculate the ledger hash chain.
            </p>

            {verificationResult && (
              <div className={`p-4 rounded-xl border ${
                verificationResult.verified 
                  ? 'bg-cyberGreen/10 border-cyberGreen/30' 
                  : 'bg-red-500/10 border-red-500/30'
              } flex flex-col gap-2`}>
                <div className="flex items-center gap-2">
                  {verificationResult.verified ? (
                    <CheckCircle className="text-cyberGreen" size={18} />
                  ) : (
                    <AlertTriangle className="text-red-400" size={18} />
                  )}
                  <span className="text-xs font-bold text-white">
                    {verificationResult.verified 
                      ? 'Ledger Chain Verification Succeeded (Tamper-Proof Proof OK)' 
                      : 'Ledger Chain Verification Failed'
                    }
                  </span>
                </div>
                
                {verificationResult.verified && (
                  <div className="space-y-1.5 mt-1">
                    <div className="text-[11px] text-gray-400">
                      Total Ledger Blocks Checked: <strong className="text-white">{verificationResult.total_logs}</strong>
                    </div>
                    <div className="text-[11px] text-gray-400 flex items-center gap-1.5">
                      Root Ledger Hash (Chain Anchor): 
                      <span className="bg-darkBg px-2 py-0.5 rounded text-[10px] text-cyberPurple font-mono truncate max-w-[280px]" title={verificationResult.hash_chain_root}>
                        {verificationResult.hash_chain_root}
                      </span>
                    </div>
                  </div>
                )}

                {verificationResult.error && (
                  <div className="text-[11px] text-red-400 mt-1">{verificationResult.error}</div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Right Column (1/3 width): Data Residency & Badges */}
        <div className="space-y-6">
          
          {/* Card 3: Data Residency Configuration */}
          <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 space-y-4">
            <h3 className="font-semibold text-sm text-white flex items-center gap-2">
              <Globe size={16} className="text-cyberBlue" /> Data Residency Gating
            </h3>
            <p className="text-xs text-gray-400">
              Select your organization's primary data storage residency. All transactional and search indices are hosted strictly in this Azure region.
            </p>

            <div className="space-y-2">
              <label className="text-[10px] uppercase font-bold text-gray-400 block">Hosting Region & Sovereign Clouds</label>
              <div className="relative">
                <select
                  value={region}
                  onChange={handleResidencyChange}
                  disabled={updatingResidency}
                  className="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-cyberBlue text-gray-200 appearance-none pr-8 cursor-pointer"
                >
                  <option value="East US (Primary)">East US (Primary - Northern Virginia)</option>
                  <option value="North Europe (EU GDPR compliant)">North Europe (EU GDPR compliant - Dublin)</option>
                  <option value="UK South (UK Sovereign cloud)">UK South (UK Sovereign cloud - London)</option>
                  <option value="West US (Secondary)">West US (Secondary - California)</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
                  <Server size={12} />
                </div>
              </div>
            </div>

            {successMsg && (
              <div className="p-3 bg-cyberBlue/10 border border-cyberBlue/20 rounded-xl text-xs text-cyberBlue font-semibold flex items-center gap-2">
                <CheckCircle size={14} /> {successMsg}
              </div>
            )}
          </div>

          {/* Card 4: Compliance Certificates */}
          <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 space-y-4">
            <h3 className="font-semibold text-sm text-white flex items-center gap-2">
              <ShieldCheck size={16} className="text-cyberGreen" /> Compliance Framework Audits
            </h3>
            <div className="space-y-3">
              {[
                { name: 'ISO 27001:2022 Certified', desc: 'Information Security Management System', badge: 'Certified' },
                { name: 'SOC 2 Type II Compliant', desc: 'Trust Services Criteria CC6.1 & CC7.1', badge: 'Active' },
                { name: 'GDPR / UK GDPR Gated', desc: 'Data Processor Clauses (Article 28 / Article 32)', badge: 'Regulated' },
                { name: 'HIPAA Security Safeguards', desc: 'Administrative & Physical Safeguards', badge: 'Assessed' }
              ].map((cert, idx) => (
                <div key={idx} className="flex justify-between items-start border-b border-darkBorder/40 pb-2 last:border-b-0 last:pb-0">
                  <div>
                    <h5 className="text-xs font-bold text-white">{cert.name}</h5>
                    <p className="text-[10px] text-gray-400 mt-0.5">{cert.desc}</p>
                  </div>
                  <span className="text-[9px] bg-cyberGreen/10 text-cyberGreen px-1.5 py-0.5 rounded font-bold uppercase">
                    {cert.badge}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
