import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { Shield, Search, RefreshCw, Terminal, Eye, AlertOctagon } from 'lucide-react';

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLog, setSelectedLog] = useState<any | null>(null);
  const [riskFilter, setRiskFilter] = useState('ALL');

  const fetchAuditLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAuditLogs();
      setLogs(data);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve system audit logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    const matchesSearch = 
      log.action.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (log.ip_address && log.ip_address.includes(searchQuery)) ||
      (log.query_hash && log.query_hash.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (log.user_entra_id && log.user_entra_id.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesRisk = 
      riskFilter === 'ALL' || 
      (log.risk_level && log.risk_level.toUpperCase() === riskFilter.toUpperCase());

    return matchesSearch && matchesRisk;
  });

  const getRiskBadgeStyles = (risk: string) => {
    if (!risk) return 'bg-gray-800 text-gray-400';
    switch (risk.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'bg-red-500/10 border border-red-500/20 text-red-400 shadow-glow';
      case 'medium':
        return 'bg-amber-500/10 border border-amber-500/20 text-amber-400';
      case 'low':
      default:
        return 'bg-cyberGreen/10 border border-cyberGreen/20 text-cyberGreen shadow-glowGreen';
    }
  };

  return (
    <div className="flex-1 p-6 md:p-8 bg-[#0a0d16] overflow-y-auto space-y-6">
      
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-wide font-outfit uppercase">
            Tenant Audit Trails
          </h1>
          <p className="text-xs text-gray-400">
            Immutable, tenant-isolated activity registers tracking user authentication actions, policy evaluations, and AI agent calls.
          </p>
        </div>
        
        <button
          onClick={fetchAuditLogs}
          className="flex items-center gap-2 px-4 py-2.5 bg-darkCard hover:bg-[#1a2336] border border-darkBorder text-gray-300 hover:text-white rounded-xl text-xs font-bold transition duration-300 shadow-glow"
        >
          <RefreshCw size={14} />
          Refresh Registry
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl text-xs font-semibold">
          {error}
        </div>
      )}

      {/* Analytics Mini Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 bg-darkCard border border-darkBorder rounded-3xl relative overflow-hidden">
          <span className="text-[10px] text-gray-400 font-mono uppercase tracking-widest block mb-2">Total Queries Audit-Logged</span>
          <span className="text-3xl font-extrabold text-white font-outfit">{logs.length}</span>
          <div className="absolute right-4 bottom-4 text-cyberBlue/10"><Terminal size={48} /></div>
        </div>
        <div className="p-5 bg-darkCard border border-darkBorder rounded-3xl relative overflow-hidden">
          <span className="text-[10px] text-gray-400 font-mono uppercase tracking-widest block mb-2">High/Critical Alerts</span>
          <span className="text-3xl font-extrabold text-red-400 font-outfit">
            {logs.filter(l => l.risk_level?.toLowerCase() === 'high' || l.risk_level?.toLowerCase() === 'critical').length}
          </span>
          <div className="absolute right-4 bottom-4 text-red-500/10"><AlertOctagon size={48} /></div>
        </div>
        <div className="p-5 bg-darkCard border border-darkBorder rounded-3xl relative overflow-hidden">
          <span className="text-[10px] text-gray-400 font-mono uppercase tracking-widest block mb-2">Unique IP Addresses</span>
          <span className="text-3xl font-extrabold text-cyberGreen font-outfit">
            {new Set(logs.map(l => l.ip_address).filter(Boolean)).size}
          </span>
          <div className="absolute right-4 bottom-4 text-cyberGreen/10"><Shield size={48} /></div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 bg-darkCard border border-darkBorder rounded-2xl">
        <div className="relative flex-1 max-w-md">
          <Search size={14} className="absolute left-3.5 top-3.5 text-gray-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by action, IP address, SHA hash, user..."
            className="w-full pl-10 pr-4 py-2.5 bg-[#0a0d16] border border-darkBorder rounded-xl text-xs text-white focus:outline-none focus:border-cyberBlue transition"
          />
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-gray-400 font-mono uppercase tracking-widest">Risk Severity:</span>
          <div className="flex border border-darkBorder rounded-xl overflow-hidden text-xs bg-[#0a0d16]">
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((risk) => (
              <button
                key={risk}
                onClick={() => setRiskFilter(risk)}
                className={`px-3 py-1.5 font-bold transition ${
                  riskFilter === risk
                    ? 'bg-cyberBlue text-[#0a0d16]'
                    : 'text-gray-400 hover:text-white hover:bg-darkCard'
                }`}
              >
                {risk}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Datagrid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Datagrid Table */}
        <div className="lg:col-span-8 bg-darkCard border border-darkBorder rounded-3xl overflow-hidden shadow-lg">
          {loading ? (
            <div className="p-12 text-center text-gray-400 text-xs font-mono uppercase tracking-widest animate-pulse">
              Querying Tenant Cryptographic Audit Registers...
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-left">
                <thead>
                  <tr className="border-b border-darkBorder bg-[#0c101d] text-gray-400 text-[10px] uppercase font-mono tracking-wider">
                    <th className="p-4 pl-6">Timestamp</th>
                    <th className="p-4">Action</th>
                    <th className="p-4">Risk</th>
                    <th className="p-4 font-mono">IP Address</th>
                    <th className="p-4 pr-6 text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-darkBorder/40">
                  {filteredLogs.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="p-8 text-center text-xs text-gray-500 font-mono">
                        No audit events match the active filter criteria.
                      </td>
                    </tr>
                  ) : (
                    filteredLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-darkCard/50 text-xs transition duration-150">
                        <td className="p-4 pl-6 text-gray-400 font-mono text-[10px]">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                        <td className="p-4 font-bold text-white max-w-[180px] truncate">{log.action}</td>
                        <td className="p-4">
                          <span className={`px-2 py-0.5 rounded-full text-[9px] font-extrabold uppercase ${getRiskBadgeStyles(log.risk_level)}`}>
                            {log.risk_level || 'low'}
                          </span>
                        </td>
                        <td className="p-4 text-gray-300 font-mono">{log.ip_address || '127.0.0.1'}</td>
                        <td className="p-4 pr-6 text-right">
                          <button
                            onClick={() => setSelectedLog(log)}
                            className="p-2 text-cyberBlue hover:bg-cyberBlue/10 rounded-xl transition duration-200"
                            title="Inspect Log Block"
                          >
                            <Eye size={14} />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Detailed Inspector Panel */}
        <div className="lg:col-span-4 bg-darkCard border border-darkBorder rounded-3xl p-6 space-y-4 shadow-lg min-h-[300px]">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2 border-b border-darkBorder pb-3">
            <Terminal size={14} className="text-cyberBlue" />
            Audit Object Inspector
          </h2>
          
          {selectedLog ? (
            <div className="space-y-4 animate-fadeIn">
              <div>
                <span className="block text-[9px] text-gray-500 font-mono uppercase tracking-widest">Event Identification Hash</span>
                <span className="block text-xs font-semibold text-white font-mono break-all">{selectedLog.id}</span>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="block text-[9px] text-gray-500 font-mono uppercase tracking-widest">User ID Reference</span>
                  <span className="block text-xs text-gray-300 break-all">{selectedLog.user_id || 'N/A'}</span>
                </div>
                <div>
                  <span className="block text-[9px] text-gray-500 font-mono uppercase tracking-widest">Tenant Realm</span>
                  <span className="block text-xs font-mono text-cyberBlue">{selectedLog.tenant_id}</span>
                </div>
              </div>
              <div>
                <span className="block text-[9px] text-gray-500 font-mono uppercase tracking-widest">Action Description</span>
                <span className="block text-xs font-semibold text-white">{selectedLog.action}</span>
              </div>
              <div>
                <span className="block text-[9px] text-gray-500 font-mono uppercase tracking-widest">Client Agent (Browser)</span>
                <span className="block text-[10px] text-gray-400 break-words leading-relaxed font-mono bg-[#0a0d16] p-2.5 rounded-xl border border-darkBorder">
                  {selectedLog.user_agent || 'Unknown User-Agent'}
                </span>
              </div>
              {selectedLog.query_hash && (
                <div>
                  <span className="block text-[9px] text-gray-500 font-mono uppercase tracking-widest">SHA-256 Telemetry Hash</span>
                  <span className="block text-[10px] font-mono text-cyberPurple break-all bg-[#0a0d16] p-2.5 rounded-xl border border-darkBorder">
                    {selectedLog.query_hash}
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12 text-xs text-gray-500 font-mono">
              Select an audit log entry from the grid to inspect the underlying security block payload.
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
