import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../lib/AuthContext';
import { ShieldAlert, ArrowLeft } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission?: string;
  allowedRoles?: string[];
}

export default function ProtectedRoute({ children, requiredPermission, allowedRoles }: ProtectedRouteProps) {
  const { user, loading, hasPermission, hasRole } = useAuth();

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#0a0d16] text-gray-200">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 rounded-full border-4 border-t-cyberBlue border-r-transparent border-b-transparent border-l-transparent animate-spin" />
          <div className="absolute inset-2 rounded-full border-4 border-b-cyberPurple border-t-transparent border-r-transparent border-l-transparent animate-spin duration-1000" />
        </div>
        <p className="mt-4 font-outfit text-sm font-semibold tracking-widest text-gray-400 uppercase animate-pulse">
          Decrypting Security Session...
        </p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  let authorized = true;

  if (requiredPermission) {
    authorized = hasPermission(requiredPermission);
  }

  if (allowedRoles && allowedRoles.length > 0) {
    authorized = authorized && allowedRoles.some(role => hasRole(role));
  }

  if (!authorized) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 bg-[#0a0d16] text-center relative overflow-hidden">
        {/* Glow effect */}
        <div className="absolute w-96 h-96 bg-red-500/10 rounded-full blur-[100px] pointer-events-none" />

        <div className="z-10 max-w-md bg-darkCard border border-red-500/20 p-8 rounded-3xl shadow-glowPurple relative">
          <div className="mx-auto w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center text-red-500 mb-6 border border-red-500/20">
            <ShieldAlert size={32} className="animate-bounce" />
          </div>

          <h2 className="text-2xl font-extrabold text-white mb-2 font-outfit tracking-wide uppercase">
            Access Gated
          </h2>
          <p className="text-xs text-red-400/80 font-mono mb-4">
            ERROR_CODE: HTTP_403_FORBIDDEN
          </p>

          <p className="text-gray-400 text-sm mb-8 leading-relaxed">
            Your role (<strong className="text-gray-200">{user.role.role_name}</strong>) does not possess the permissions required to view this administrative resource. This security boundary breach has been logged to the tenant audit trail.
          </p>

          <button
            onClick={() => window.location.href = '/'}
            className="w-full flex items-center justify-center gap-2 px-5 py-3 bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 text-white rounded-xl text-xs font-bold transition duration-300 shadow-glow"
          >
            <ArrowLeft size={14} />
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
