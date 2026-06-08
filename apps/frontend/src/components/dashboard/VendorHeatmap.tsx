import React from 'react';
import { ShieldCheck, ShieldAlert, CheckCircle2, XCircle } from 'lucide-react';
import { Vendor } from '../../lib/types';

interface HeatmapProps {
  vendors: Vendor[];
}

export default function VendorHeatmap({ vendors }: HeatmapProps) {
  // If no vendors are loaded, use default mock list
  const activeVendors = vendors.length > 0 ? vendors : [
    { id: '1', name: 'CollaborationHub Inc', risk_score: 38, risk_level: 'low', iso27001_certified: true, soc2_type2: true, gdpr_dpa_signed: true },
    { id: '2', name: 'Legacy CRM Tools', risk_score: 78, risk_level: 'high', iso27001_certified: false, soc2_type2: false, gdpr_dpa_signed: false },
    { id: '3', name: 'MarketingAnalytics Pro', risk_score: 52, risk_level: 'medium', iso27001_certified: true, soc2_type2: false, gdpr_dpa_signed: true }
  ] as Vendor[];

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return 'text-red-500 bg-red-500/10 border-red-500/20';
      case 'high': return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
      case 'medium': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      default: return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
    }
  };

  return (
    <div className="bg-darkCard border border-darkBorder rounded-2xl p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h4 className="font-semibold text-sm text-gray-200">Third-Party TPRM Risk Grid</h4>
        <span className="text-[10px] bg-cyberBlue/10 text-cyberBlue px-2 py-0.5 rounded-full font-medium">TPRM Active</span>
      </div>

      <div className="grid gap-3">
        {activeVendors.map(vendor => (
          <div 
            key={vendor.id} 
            className="flex items-center justify-between p-3 rounded-xl bg-darkBg border border-darkBorder/40 hover:border-darkBorder transition duration-200"
          >
            <div className="flex flex-col gap-1">
              <span className="text-xs font-semibold text-gray-200">{vendor.name}</span>
              {/* Certifications badges */}
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className={`text-[9px] flex items-center gap-0.5 ${vendor.iso27001_certified ? 'text-emerald-400' : 'text-gray-500'}`}>
                  ISO 27001 {vendor.iso27001_certified ? <CheckCircle2 size={9} /> : <XCircle size={9} />}
                </span>
                <span className="w-1 h-1 bg-gray-600 rounded-full" />
                <span className={`text-[9px] flex items-center gap-0.5 ${vendor.soc2_type2 ? 'text-emerald-400' : 'text-gray-500'}`}>
                  SOC 2 {vendor.soc2_type2 ? <CheckCircle2 size={9} /> : <XCircle size={9} />}
                </span>
                <span className="w-1 h-1 bg-gray-600 rounded-full" />
                <span className={`text-[9px] flex items-center gap-0.5 ${vendor.gdpr_dpa_signed ? 'text-emerald-400' : 'text-gray-500'}`}>
                  DPA {vendor.gdpr_dpa_signed ? <CheckCircle2 size={9} /> : <XCircle size={9} />}
                </span>
              </div>
            </div>

            {/* Score Badge */}
            <div className="flex items-center gap-2">
              <div className={`px-2 py-1 rounded-lg border text-[10px] font-mono font-bold ${getRiskColor(vendor.risk_level)}`}>
                {vendor.risk_score} / 100
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
