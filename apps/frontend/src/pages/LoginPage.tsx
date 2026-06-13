import React, { useState } from 'react';
import { useAuth } from '../lib/AuthContext';
import { Shield, Key, Mail, Lock, Sparkles, Building2 } from 'lucide-react';

export default function LoginPage() {
  const { login, loginSSO } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [tenantId, setTenantId] = useState('tenant-alpha');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Pre-configured role profiles for developer convenience
  const devProfiles = [
    { label: 'Super Admin', email: 'admin@securecop.com', role: 'Super Admin', tenant: 'tenant-alpha', desc: 'Global platform settings & logs' },
    { label: 'CISO Alpha', email: 'ciso@securecop.com', role: 'CISO', tenant: 'tenant-alpha', desc: 'All metrics & TPRM' },
    { label: 'CISO Beta', email: 'ciso.beta@securecop.com', role: 'CISO', tenant: 'tenant-beta', desc: 'Tenant Beta isolation' },
    { label: 'Security Auditor', email: 'auditor@securecop.com', role: 'Security Auditor', tenant: 'tenant-alpha', desc: 'Read-only compliance & reports' },
    { label: 'HR Manager', email: 'hr@securecop.com', role: 'HR Manager', tenant: 'tenant-alpha', desc: 'Awareness training' },
    { label: 'Compliance Officer', email: 'compliance@securecop.com', role: 'Compliance Officer', tenant: 'tenant-alpha', desc: 'Compliance dashboards' },
    { label: 'General Employee', email: 'employee@securecop.com', role: 'General Employee', tenant: 'tenant-alpha', desc: 'General features' }
  ];

  const handleProfileSelect = (prof: typeof devProfiles[0]) => {
    setEmail(prof.email);
    setPassword('password123');
    setTenantId(prof.tenant);
  };

  const handleLocalLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSSOLogin = async (roleName: string, selectedTenant: string) => {
    setError(null);
    setIsSubmitting(true);
    try {
      // Simulate OAuth 2.0 flow authorization code exchange
      const mockOAuthCode = `mock_oauth_code_${Math.random().toString(36).substring(7)}`;
      await loginSSO(mockOAuthCode, selectedTenant, roleName);
    } catch (err: any) {
      setError(err.message || 'Azure Entra ID SSO login simulation failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-screen w-screen h-screen bg-[#0a0d16] text-gray-200 flex flex-col justify-center items-center relative overflow-hidden font-sans p-4">
      {/* Background neon glows */}
      <div className="absolute top-[-20%] left-[-20%] w-[60%] h-[60%] bg-[#00d2ff] opacity-10 rounded-full blur-[140px] pointer-events-none animate-pulse-glow" />
      <div className="absolute bottom-[-20%] right-[-20%] w-[60%] h-[60%] bg-[#9d4edd] opacity-10 rounded-full blur-[140px] pointer-events-none animate-pulse-glow" />

      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 items-stretch">
        
        {/* Left Side: Brand Banner */}
        <div className="lg:col-span-5 flex flex-col justify-between p-8 rounded-3xl bg-gradient-to-br from-[#0c101d] to-[#121724]/60 border border-darkBorder relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyberBlue/5 rounded-full blur-3xl" />
          
          {/* Logo & Header */}
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-tr from-cyberBlue to-cyberPurple p-3 rounded-2xl text-white shadow-glow">
              <Shield size={28} />
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-lg text-white tracking-widest font-outfit uppercase">
                SecureCopilot 365
              </span>
              <span className="text-[10px] text-cyberBlue font-mono uppercase tracking-wider">
                Enterprise IAM Platform
              </span>
            </div>
          </div>

          {/* Marketing text */}
          <div className="my-8 space-y-4">
            <h1 className="text-3xl font-extrabold text-white font-outfit leading-tight tracking-wide">
              Secure Guardrails for <span className="bg-gradient-to-r from-cyberBlue to-cyberPurple bg-clip-text text-transparent">M365 Cloud Telemetry</span>
            </h1>
            <p className="text-xs text-gray-400 leading-relaxed">
              Deploying multi-tenant isolation, cryptographically hashed access logs, and role-based policies across security analytics dashboards.
            </p>
          </div>

          {/* Footer Metadata */}
          <div className="text-[10px] font-mono text-gray-500 border-t border-darkBorder pt-4">
            SYSTEM STATUS: <span className="text-cyberGreen font-semibold">ONLINE</span><br/>
            ACTIVE COMPLIANCE GATES: ISO27001, SOC2 TYPE II, GDPR
          </div>
        </div>

        {/* Right Side: Login Portals */}
        <div className="lg:col-span-7 flex flex-col justify-center gap-6">
          <div className="p-8 rounded-3xl bg-gradient-to-br from-[#0c101d] to-[#121724]/80 border border-darkBorder shadow-xl relative">
            <h2 className="text-xl font-bold text-white font-outfit mb-6 flex items-center gap-2">
              <Sparkles size={18} className="text-cyberBlue" />
              Access Control Gateway
            </h2>

            {error && (
              <div className="mb-5 p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl text-xs font-semibold animate-pulse">
                {error}
              </div>
            )}

            {/* Simulated Azure Entra ID Button */}
            <button
              onClick={() => handleSSOLogin('General Employee', tenantId)}
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-3 px-5 py-4 bg-gradient-to-r from-darkCard to-[#1a2336] hover:to-[#222e47] border border-darkBorder hover:border-cyberBlue/50 text-white rounded-xl text-xs font-bold transition-all duration-300 shadow-glow mb-6 disabled:opacity-50"
            >
              <svg className="w-4 h-4 mr-1" viewBox="0 0 23 23" fill="currentColor">
                <path d="M0 0h11v11H0z" fill="#f25022"/>
                <path d="M12 0h11v11H12z" fill="#7fba00"/>
                <path d="M0 12h11v11H0z" fill="#00a4ef"/>
                <path d="M12 12h11v11H12z" fill="#ffb900"/>
              </svg>
              Sign in with Azure Entra ID (SSO)
            </button>

            <div className="relative flex py-3 items-center mb-6">
              <div className="flex-grow border-t border-darkBorder"></div>
              <span className="flex-shrink mx-4 text-gray-500 text-[10px] uppercase font-mono tracking-widest">Or Local Developer Portal</span>
              <div className="flex-grow border-t border-darkBorder"></div>
            </div>

            {/* Local Login Form */}
            <form onSubmit={handleLocalLogin} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 font-mono">
                  Tenant Realm
                </label>
                <div className="relative">
                  <Building2 size={14} className="absolute left-4 top-3.5 text-gray-500" />
                  <select
                    value={tenantId}
                    onChange={(e) => setTenantId(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-[#0c101d] border border-darkBorder rounded-xl text-xs text-white focus:outline-none focus:border-cyberBlue transition font-mono"
                  >
                    <option value="tenant-alpha">Tenant Alpha (Workspace Alpha)</option>
                    <option value="tenant-beta">Tenant Beta (Workspace Beta)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 font-mono">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail size={14} className="absolute left-4 top-3.5 text-gray-500" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="name@securecop.com"
                      required
                      className="w-full pl-10 pr-4 py-3 bg-[#0c101d] border border-darkBorder rounded-xl text-xs text-white focus:outline-none focus:border-cyberBlue transition"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2 font-mono">
                    Password
                  </label>
                  <div className="relative">
                    <Lock size={14} className="absolute left-4 top-3.5 text-gray-500" />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      className="w-full pl-10 pr-4 py-3 bg-[#0c101d] border border-darkBorder rounded-xl text-xs text-white focus:outline-none focus:border-cyberBlue transition"
                    />
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center gap-2 px-5 py-3.5 bg-gradient-to-r from-cyberBlue to-cyberPurple text-white rounded-xl text-xs font-bold transition duration-300 shadow-glow hover:scale-[1.01] hover:brightness-110 disabled:opacity-50 mt-6"
              >
                <Key size={14} />
                {isSubmitting ? 'Authenticating Gateway...' : 'Initialize Local Secure Session'}
              </button>
            </form>
          </div>

          {/* Quick-Select Dev Profiles */}
          <div className="p-6 rounded-3xl bg-[#0c101d]/60 border border-darkBorder">
            <h3 className="text-xs font-bold text-cyberBlue uppercase tracking-wider mb-4 font-mono flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-cyberBlue animate-ping" />
              Quick Developer Identity Templates
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {devProfiles.map((prof) => (
                <button
                  key={prof.email}
                  onClick={() => handleProfileSelect(prof)}
                  className="p-3 text-left bg-darkCard hover:bg-[#1a2336] border border-darkBorder hover:border-cyberPurple/50 rounded-xl transition duration-200 group flex flex-col justify-between"
                >
                  <div>
                    <span className="block text-[10px] font-bold text-white group-hover:text-cyberBlue transition">
                      {prof.label}
                    </span>
                    <span className="block text-[8px] text-gray-500 font-mono mt-1">
                      {prof.tenant}
                    </span>
                  </div>
                  <span className="block text-[8px] text-gray-400 mt-2 line-clamp-1">
                    {prof.desc}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
