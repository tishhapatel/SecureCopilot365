import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserResponse } from './types';

interface AuthContextType {
  user: UserResponse | null;
  accessToken: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginSSO: (code: string, tenantId?: string, roleName?: string) => Promise<void>;
  logout: () => void;
  hasPermission: (permissionName: string) => boolean;
  hasRole: (roleName: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Initialize Auth state from localStorage
  useEffect(() => {
    async function initializeAuth() {
      const storedToken = localStorage.getItem('securecop_access_token');
      const storedRefreshToken = localStorage.getItem('securecop_refresh_token');
      const storedUser = localStorage.getItem('securecop_user');

      if (storedToken && storedUser) {
        setAccessToken(storedToken);
        setUser(JSON.parse(storedUser));
      }

      // If refresh token exists, try to perform a token refresh on mount to verify session
      if (storedRefreshToken) {
        try {
          const res = await fetch('/api/v1/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: storedRefreshToken })
          });
          if (res.ok) {
            const data = await res.json();
            localStorage.setItem('securecop_access_token', data.access_token);
            localStorage.setItem('securecop_refresh_token', data.refresh_token);
            localStorage.setItem('securecop_user', JSON.stringify(data.user));
            setAccessToken(data.access_token);
            setUser(data.user);
          } else {
            // Refresh token expired or invalid, log out
            localStorage.removeItem('securecop_access_token');
            localStorage.removeItem('securecop_refresh_token');
            localStorage.removeItem('securecop_user');
            setAccessToken(null);
            setUser(null);
          }
        } catch (e) {
          console.error('Failed to auto-refresh session:', e);
        }
      }
      setLoading(false);
    }
    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Login failed. Invalid credentials.');
      }
      const data = await res.json();
      localStorage.setItem('securecop_access_token', data.access_token);
      localStorage.setItem('securecop_refresh_token', data.refresh_token);
      localStorage.setItem('securecop_user', JSON.stringify(data.user));
      setAccessToken(data.access_token);
      setUser(data.user);
    } finally {
      setLoading(false);
    }
  };

  const loginSSO = async (code: string, tenantId?: string, roleName?: string) => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/auth/entra/callback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, tenant_id: tenantId, role_name: roleName })
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'SSO callback failed.');
      }
      const data = await res.json();
      localStorage.setItem('securecop_access_token', data.access_token);
      localStorage.setItem('securecop_refresh_token', data.refresh_token);
      localStorage.setItem('securecop_user', JSON.stringify(data.user));
      setAccessToken(data.access_token);
      setUser(data.user);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('securecop_access_token');
    localStorage.removeItem('securecop_refresh_token');
    localStorage.removeItem('securecop_user');
    setAccessToken(null);
    setUser(null);
  };

  const hasPermission = (permissionName: string): boolean => {
    if (!user) return false;
    if (user.role.role_name === 'Super Admin') return true;
    return user.role.permissions.some((p: any) => p.permission_name === permissionName);
  };

  const hasRole = (roleName: string): boolean => {
    if (!user) return false;
    return user.role.role_name === roleName || user.role.role_name === 'Super Admin';
  };

  return (
    <AuthContext.Provider value={{ user, accessToken, loading, login, loginSSO, logout, hasPermission, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
