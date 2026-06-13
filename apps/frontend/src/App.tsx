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
  Menu,
  UserCog,
  Terminal,
  Layers,
  LogOut,
  ShieldCheck
} from 'lucide-react';

import { AuthProvider, useAuth } from './lib/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import PhishingPage from './pages/PhishingPage';
import CompliancePage from './pages/CompliancePage';
import VendorPage from './pages/VendorPage';
import AuditPage from './pages/AuditPage';
import AwarenessPage from './pages/AwarenessPage';
import UserManagementPage from './pages/admin/UserManagementPage';
import PermissionMatrixPage from './pages/admin/PermissionMatrixPage';
import AuditLogsPage from './pages/admin/AuditLogsPage';
import ChatInterface from './components/chat/ChatInterface';
import TrustCenter from './pages/TrustCenter';

function Navigation() {
  const location = useLocation();
  const { hasPermission } = useAuth();
  
  const navItems = [
    { path: '/', label: 'CISO Dashboard', icon: LayoutDashboard },
    { path: '/trust-center', label: 'Trust Center', icon: ShieldCheck },
    { path: '/phishing', label: 'Phishing Detection', icon: ShieldAlert, permission: 'SUBMIT_REPORTS' },
    { path: '/compliance', label: 'Compliance Advisor', icon: FileCheck, permission: 'VIEW_COMPLIANCE' },
    { path: '/vendor', label: 'TPRM Vendor Risk', icon: Building2, permission: 'VIEW_VENDORS' },
    { path: '/audit', label: 'Audit Readiness', icon: ClipboardCheck, permission: 'VIEW_AUDITS' },
    { path: '/awareness', label: 'Awareness Coach', icon: GraduationCap, permission: 'RUN_AWARENESS' },
    { path: '/admin/users', label: 'User Directory', icon: UserCog, permission: 'MANAGE_USERS' },
    { path: '/admin/matrix', label: 'Permission Matrix', icon: Layers, permission: 'MANAGE_USERS' },
    { path: '/admin/logs', label: 'Audit Logs', icon: Terminal, permission: 'VIEW_AUDITS' },
  ];

  const filteredItems = navItems.filter(item => {
    if (item.permission && !hasPermission(item.permission)) {
      return false;
    }
    return true;
  });

  return (
    <nav className="space-y-1">
      {filteredItems.map((item) => {
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

function AppContent() {
  const { user, loading, logout } = useAuth();
  const [chatOpen, setChatOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  if (loading) {
    return (
      <div className="flex h-screen w-screen bg-[#0a0d16] text-gray-200 justify-center items-center font-sans">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 rounded-full border-4 border-t-cyberBlue border-r-transparent border-b-transparent border-l-transparent animate-spin" />
          <div className="absolute inset-2 rounded-full border-4 border-b-cyberPurple border-t-transparent border-r-transparent border-l-transparent animate-spin duration-1000" />
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  const initials = user.display_name
    .split(' ')
    .map((n: string) => n[0])
    .join('')
    .substring(0, 2)
    .toUpperCase();

  return (
    <div className="flex h-screen w-screen bg-[#0a0d16] text-gray-200 overflow-hidden font-sans relative">
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
        <div className="p-4 border-t border-darkBorder bg-darkCard/20 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#9d4edd] to-[#00d2ff] flex items-center justify-center font-bold text-xs text-white flex-shrink-0">
              {initials || 'U'}
            </div>
            <div className="flex flex-col overflow-hidden">
              <span className="text-xs font-semibold text-white truncate max-w-[120px]" title={user.display_name}>
                {user.display_name}
              </span>
              <span className="text-[10px] text-gray-400 truncate max-w-[120px]" title={user.role.role_name}>
                {user.role.role_name}
              </span>
            </div>
          </div>
          
          <button 
            onClick={logout}
            className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition duration-150 flex-shrink-0"
            title="Sign Out"
          >
            <LogOut size={14} />
          </button>
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
          <Route path="/trust-center" element={<TrustCenter />} />
          <Route path="/phishing" element={<ProtectedRoute requiredPermission="SUBMIT_REPORTS"><PhishingPage /></ProtectedRoute>} />
          <Route path="/compliance" element={<ProtectedRoute requiredPermission="VIEW_COMPLIANCE"><CompliancePage /></ProtectedRoute>} />
          <Route path="/vendor" element={<ProtectedRoute requiredPermission="VIEW_VENDORS"><VendorPage /></ProtectedRoute>} />
          <Route path="/audit" element={<ProtectedRoute requiredPermission="VIEW_AUDITS"><AuditPage /></ProtectedRoute>} />
          <Route path="/awareness" element={<ProtectedRoute requiredPermission="RUN_AWARENESS"><AwarenessPage /></ProtectedRoute>} />
          <Route path="/admin/users" element={<ProtectedRoute requiredPermission="MANAGE_USERS"><UserManagementPage /></ProtectedRoute>} />
          <Route path="/admin/matrix" element={<ProtectedRoute requiredPermission="MANAGE_USERS"><PermissionMatrixPage /></ProtectedRoute>} />
          <Route path="/admin/logs" element={<ProtectedRoute requiredPermission="VIEW_AUDITS"><AuditLogsPage /></ProtectedRoute>} />
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
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}
