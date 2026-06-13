import { DashboardSummaryResponse, PhishingIncident, Vendor, ComplianceQuery, AuditReport } from './types';

const BASE_URL = '/api/v1';

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const token = localStorage.getItem('securecop_access_token');
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : 'Bearer mock-token-12345',
      ...(options?.headers || {})
    }
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json() as T;
}

export const api = {
  getDashboardSummary: async (): Promise<DashboardSummaryResponse> => {
    try {
      return await fetchJson<DashboardSummaryResponse>('/dashboard/summary');
    } catch (e) {
      console.warn("API summary query failed. Returning fallback mock summary.", e);
      return {
        risk_metrics: { organization_risk_score: 35.0, average_awareness_score: 75.0, total_monitored_employees: 10 },
        phishing_scans: { total_scanned: 25, critical_threats: 3, high_threats: 7, user_reports: 12 },
        vendor_tprm: { total_vendors: 14, by_tier: { critical: 1, high: 3, medium: 6, low: 4 } },
        audit_readiness: { iso27001_readiness: 74.0, controls_evidenced: 69, controls_total: 93, readiness_band: 'mostly_ready' },
        recent_threats_feed: [
          { id: 1, source: 'Outlook', type: 'Spearphishing Link', target: 'Finance Department', timestamp: '10 mins ago', risk: 'critical' },
          { id: 2, source: 'SharePoint', type: 'GDPR Compliance Gap', target: 'Data Privacy Policy', timestamp: '1 hour ago', risk: 'high' },
          { id: 3, source: 'Teams', type: 'MFA Disabled Alarm', target: 'External Contractor', timestamp: '3 hours ago', risk: 'high' },
          { id: 4, source: 'TPRM', type: 'Vendor Incident', target: 'Hosting Sub-processor', timestamp: '5 hours ago', risk: 'medium' }
        ]
      };
    }
  },
  
  getPhishingIncidents: async (): Promise<PhishingIncident[]> => {
    try {
      return await fetchJson<PhishingIncident[]>('/phishing/incidents');
    } catch {
      return [];
    }
  },

  scanEmail: async (emailData: any): Promise<any> => {
    return await fetchJson<any>('/phishing/scan', {
      method: 'POST',
      body: JSON.stringify(emailData)
    });
  },

  getVendors: async (): Promise<Vendor[]> => {
    try {
      return await fetchJson<Vendor[]>('/vendor/list');
    } catch {
      return [];
    }
  },

  assessVendor: async (vendorData: any): Promise<any> => {
    return await fetchJson<any>('/vendor/assess', {
      method: 'POST',
      body: JSON.stringify(vendorData)
    });
  },

  getComplianceQueries: async (): Promise<ComplianceQuery[]> => {
    try {
      return await fetchJson<ComplianceQuery[]>('/compliance/queries');
    } catch {
      return [];
    }
  },

  checkCompliance: async (docData: any): Promise<any> => {
    return await fetchJson<any>('/compliance/check', {
      method: 'POST',
      body: JSON.stringify(docData)
    });
  },

  getAuditReports: async (): Promise<AuditReport[]> => {
    try {
      return await fetchJson<AuditReport[]>('/audit/reports');
    } catch {
      return [];
    }
  },

  evaluateAudit: async (auditData: any): Promise<any> => {
    return await fetchJson<any>('/audit/evaluate', {
      method: 'POST',
      body: JSON.stringify(auditData)
    });
  },

  getTrainingScenario: async (topic?: string): Promise<any> => {
    return await fetchJson<any>('/awareness/scenario', {
      method: 'POST',
      body: JSON.stringify({ topic })
    });
  },

  submitTrainingAnswer: async (topic: string, correct: boolean): Promise<any> => {
    return await fetchJson<any>('/awareness/submit', {
      method: 'POST',
      body: JSON.stringify({ topic, correct })
    });
  },

  sendCopilotChat: async (query: string, fileData?: any): Promise<any> => {
    return await fetchJson<any>('/agents/chat', {
      method: 'POST',
      body: JSON.stringify({ query, file_data: fileData })
    });
  },

  getUsers: async (): Promise<any[]> => {
    return await fetchJson<any[]>('/auth/users');
  },

  createUser: async (userData: any): Promise<any> => {
    return await fetchJson<any>('/auth/users', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  },

  updateUserRole: async (userId: string, roleName: string): Promise<any> => {
    return await fetchJson<any>(`/auth/users/${userId}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role_name: roleName })
    });
  },

  updateUserActivation: async (userId: string, isActive: boolean): Promise<any> => {
    return await fetchJson<any>(`/auth/users/${userId}/activation`, {
      method: 'PUT',
      body: JSON.stringify({ is_active: isActive })
    });
  },

  deleteUser: async (userId: string): Promise<any> => {
    return await fetchJson<any>(`/auth/users/${userId}`, {
      method: 'DELETE'
    });
  },

  getRoles: async (): Promise<any[]> => {
    return await fetchJson<any[]>('/auth/roles');
  },

  getAuditLogs: async (): Promise<any[]> => {
    return await fetchJson<any[]>('/auth/audit_logs');
  },

  verifyAuditLedger: async (): Promise<any> => {
    return await fetchJson<any>('/audit/verify-ledger');
  },

  getDataResidency: async (): Promise<any> => {
    return await fetchJson<any>('/auth/data-residency');
  },

  updateDataResidency: async (region: string): Promise<any> => {
    return await fetchJson<any>('/auth/data-residency', {
      method: 'POST',
      body: JSON.stringify({ region })
    });
  }
};
