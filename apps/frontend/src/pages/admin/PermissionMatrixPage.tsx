import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { Shield, CheckCircle2, XCircle, RefreshCw, Key } from 'lucide-react';

export default function PermissionMatrixPage() {
  const [roles, setRoles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const permissionsList = [
    { name: 'MANAGE_TENANTS', label: 'Manage Tenants', desc: 'Partition tenant directories and data stores' },
    { name: 'MANAGE_USERS', label: 'Manage Users', desc: 'Provision profiles, assign roles, toggle activation' },
    { name: 'VIEW_INCIDENTS', label: 'View Incidents', desc: 'Browse phishing intelligence alerts and event summaries' },
    { name: 'SUBMIT_REPORTS', label: 'Submit Reports', desc: 'Submit email objects for AI security inspections' },
    { name: 'VIEW_COMPLIANCE', label: 'View Compliance', desc: 'Access compliance registers and framework mappings' },
    { name: 'RUN_COMPLIANCE', label: 'Run Compliance Check', desc: 'Upload policy documents for automated compliance review' },
    { name: 'VIEW_VENDORS', label: 'View Vendors', desc: 'Read Third-Party Risk Management registry and scores' },
    { name: 'MANAGE_VENDORS', label: 'Manage Vendors', desc: 'Register vendor assets and execute risk assessments' },
    { name: 'VIEW_AUDITS', label: 'View Audits', desc: 'View generated audit readiness packages' },
    { name: 'RUN_AUDITS', label: 'Run Audits', desc: 'Initiate audit assessment agents on selected policies' },
    { name: 'VIEW_AWARENESS', label: 'View Awareness', desc: 'Access employee training analytics and scores' },
    { name: 'ASSIGN_AWARENESS', label: 'Assign Awareness', desc: 'Deploy phishing simulations and courses' },
    { name: 'RUN_AWARENESS', label: 'Run Awareness Scenario', desc: 'Interact with awareness chatbot training simulations' }
  ];

  const fetchRoles = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getRoles();
      setRoles(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch security role mappings.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoles();
  }, []);

  const hasPermission = (role: any, permissionName: string) => {
    if (role.role_name === 'Super Admin') return true;
    return role.permissions.some((p: any) => p.permission_name === permissionName);
  };

  return (
    <div className="flex-1 p-6 md:p-8 bg-[#0a0d16] overflow-y-auto space-y-6">
      
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-wide font-outfit uppercase">
            Security Permission Matrix
          </h1>
          <p className="text-xs text-gray-400">
            Read-only visual directory of system privileges and backend route guards assigned per user classification.
          </p>
        </div>
        
        <button
          onClick={fetchRoles}
          className="flex items-center gap-2 px-4 py-2.5 bg-darkCard hover:bg-[#1a2336] border border-darkBorder text-gray-300 hover:text-white rounded-xl text-xs font-bold transition duration-300 shadow-glow"
        >
          <RefreshCw size={14} />
          Reload Roles Mapping
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl text-xs font-semibold">
          {error}
        </div>
      )}

      {/* Grid container */}
      <div className="bg-darkCard border border-darkBorder rounded-3xl overflow-hidden shadow-lg">
        {loading ? (
          <div className="p-12 text-center text-gray-400 text-xs font-mono uppercase tracking-widest animate-pulse">
            Compiling roles permission database...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left">
              <thead>
                <tr className="border-b border-darkBorder bg-[#0c101d] text-gray-400 text-[10px] uppercase font-mono tracking-wider">
                  <th className="p-4 pl-6 w-72">Permission Gate</th>
                  {roles.map((r) => (
                    <th key={r.id} className="p-4 text-center min-w-32">
                      <span className="block font-bold text-white text-[11px] whitespace-nowrap">{r.role_name}</span>
                      <span className="block text-[8px] text-gray-500 font-normal mt-0.5 line-clamp-1 max-w-[120px]">
                        {r.description}
                      </span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-darkBorder/40">
                {permissionsList.map((perm) => (
                  <tr key={perm.name} className="hover:bg-darkCard/50 text-xs transition duration-150">
                    <td className="p-4 pl-6 border-r border-darkBorder/30">
                      <div className="flex items-start gap-2">
                        <Key size={14} className="text-cyberBlue mt-0.5 flex-shrink-0" />
                        <div>
                          <span className="block font-semibold text-white font-mono text-[11px]">
                            {perm.name}
                          </span>
                          <span className="block text-[10px] text-gray-400 mt-0.5">
                            {perm.desc}
                          </span>
                        </div>
                      </div>
                    </td>
                    {roles.map((role) => {
                      const allowed = hasPermission(role, perm.name);
                      return (
                        <td key={`${role.id}-${perm.name}`} className="p-4 text-center">
                          <div className="flex justify-center">
                            {allowed ? (
                              <div className="flex items-center gap-1.5 text-cyberGreen bg-cyberGreen/5 border border-cyberGreen/20 px-2.5 py-1 rounded-full text-[9px] font-bold shadow-glowGreen">
                                <CheckCircle2 size={10} /> ALLOWED
                              </div>
                            ) : (
                              <div className="flex items-center gap-1.5 text-gray-600 bg-gray-900/10 border border-gray-900/20 px-2.5 py-1 rounded-full text-[9px] font-bold">
                                <XCircle size={10} /> DENIED
                              </div>
                            )}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
