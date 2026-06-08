import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  Shield, 
  LayoutDashboard, 
  ShieldAlert, 
  FileCheck, 
  Building2, 
  ClipboardCheck, 
  GraduationCap,
  MessageSquare,
  X,
  Menu
} from 'lucide-react';

import Dashboard from './pages/Dashboard';
import PhishingPage from './pages/PhishingPage';
import CompliancePage from './pages/CompliancePage';
import VendorPage from './pages/VendorPage';
import AuditPage from './pages/AuditPage';
import AwarenessPage from './pages/AwarenessPage';
import ChatInterface from './components/chat/ChatInterface';

function Navigation() {
  const location = useLocation();
  const navItems = [
    { path: '/', label: 'CISO Dashboard', icon: LayoutDashboard },
    { path: '/phishing', label: 'Phishing Detection', icon: ShieldAlert },
    { path: '/compliance', label: 'Compliance Advisor', icon: FileCheck },
    { path: '/vendor', label: 'TPRM Vendor Risk', icon: Building2 },
    { path: '/audit', label: 'Audit Readiness', icon: ClipboardCheck },
    { path: '/awareness', label: 'Awareness Coach', icon: GraduationCap },
  ];

  return (
    <nav className="space-y-1">
      {navItems.map((item) => {
        const Icon = item.icon;
        const isActive = location.pathname === item.path;
        return (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold transition-all ${
              isActive
                ? 'bg-cyberBlue/10 text-cyberBlue border-l-2 border-cyberBlue'
                : 'text-gray-400 hover:text-gray-200 hover:bg-darkCard/50'
            }`}
          >
            <Icon size={16} />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

export default function App() {
  const [chatOpen, setChatOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <Router>
      <div className="flex h-screen w-screen bg-[#0a0d16] text-gray-200 overflow-hidden font-sans">
        {/* Glow effect in background */}
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-[#00d2ff] opacity-10 rounded-full blur-[120px] pointer-events-none animate-pulse-glow" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-[#9d4edd] opacity-10 rounded-full blur-[120px] pointer-events-none animate-pulse-glow" />

        {/* Sidebar Left */}
        <aside className={`w-64 border-r border-darkBorder bg-[#0c101d] flex flex-col z-30 transition-transform duration-300 absolute md:relative md:translate-x-0 ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        } h-full`}>
          {/* Logo */}
          <div className="p-6 border-b border-darkBorder flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="bg-gradient-to-tr from-cyberBlue to-cyberPurple p-2 rounded-xl text-white shadow-glow">
                <Shield size={18} />
              </div>
              <span className="font-extrabold text-sm text-white tracking-wider font-outfit uppercase">
                SecureCopilot 365
              </span>
            </div>
            <button className="md:hidden text-gray-400" onClick={() => setMobileMenuOpen(false)}>
              <X size={18} />
            </button>
          </div>

          {/* Navigation */}
          <div className="flex-1 p-4 overflow-y-auto">
            <Navigation />
          </div>

          {/* User Profile */}
          <div className="p-4 border-t border-darkBorder bg-darkCard/20 flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#9d4edd] to-[#00d2ff] flex items-center justify-center font-bold text-xs text-white">
              TP
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-white">Tisha Patel</span>
              <span className="text-[10px] text-gray-400">Billing Specialist</span>
            </div>
          </div>
        </aside>

        {/* Mobile menu toggle */}
        <button 
          onClick={() => setMobileMenuOpen(true)}
          className="absolute top-4 left-4 md:hidden bg-darkCard border border-darkBorder p-2 rounded-xl text-gray-400 hover:text-white z-20"
        >
          <Menu size={18} />
        </button>

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col overflow-hidden relative min-w-0">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/phishing" element={<PhishingPage />} />
            <Route path="/compliance" element={<CompliancePage />} />
            <Route path="/vendor" element={<VendorPage />} />
            <Route path="/audit" element={<AuditPage />} />
            <Route path="/awareness" element={<AwarenessPage />} />
          </Routes>

          {/* Chat Floating toggle button */}
          {!chatOpen && (
            <button 
              onClick={() => setChatOpen(true)}
              className="absolute bottom-6 right-6 bg-gradient-to-tr from-cyberBlue to-cyberPurple text-white p-3.5 rounded-full shadow-glow z-20 hover:scale-105 transition"
            >
              <MessageSquare size={20} />
            </button>
          )}
        </main>

        {/* Sidebar Right (Copilot Chat) */}
        {chatOpen && (
          <aside className="w-80 md:w-96 border-l border-darkBorder bg-[#0c101d] flex flex-col z-20 relative h-full">
            <div className="p-4 border-b border-darkBorder flex items-center justify-between">
              <span className="font-semibold text-xs text-white uppercase tracking-wider">SecureCopilot Assistant</span>
              <button 
                onClick={() => setChatOpen(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={16} />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <ChatInterface />
            </div>
          </aside>
        )}
      </div>
    </Router>
  );
}
