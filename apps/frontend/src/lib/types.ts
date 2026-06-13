export interface RiskMetrics {
  organization_risk_score: number;
  average_awareness_score: number;
  total_monitored_employees: number;
}

export interface PhishingScans {
  total_scanned: number;
  critical_threats: number;
  high_threats: number;
  user_reports: number;
}

export interface VendorTPRM {
  total_vendors: number;
  by_tier: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}

export interface AuditReadiness {
  iso27001_readiness: number;
  controls_evidenced: number;
  controls_total: number;
  readiness_band: string;
}

export interface ThreatFeedItem {
  id: number;
  source: string;
  type: string;
  target: string;
  timestamp: string;
  risk: 'critical' | 'high' | 'medium' | 'low';
}

export interface DashboardSummaryResponse {
  risk_metrics: RiskMetrics;
  phishing_scans: PhishingScans;
  vendor_tprm: VendorTPRM;
  audit_readiness: AuditReadiness;
  recent_threats_feed: ThreatFeedItem[];
}

export interface PhishingIncident {
  id: string;
  employee_id: string;
  email_subject: string;
  sender_domain: string;
  risk_score: number;
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  mitre_techniques: string; // JSON string array
  indicators: string; // JSON object array
  user_action: string;
  reported_to_soc: boolean;
  analyzed_at: string;
}

export interface Vendor {
  id: string;
  name: string;
  website?: string;
  data_categories?: string; // JSON string array
  risk_score: number;
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  iso27001_certified: boolean;
  soc2_type2: boolean;
  gdpr_dpa_signed: boolean;
  last_assessment_date?: string;
  sub_processors?: string; // JSON string array
  questionnaire_score?: number;
  notes?: string;
}

export interface ComplianceQuery {
  id: string;
  employee_id?: string;
  document_name?: string;
  frameworks_checked?: string; // JSON string array
  gaps_found: number;
  gap_details?: string; // JSON objects
  citations?: string; // JSON string array
  query_at: string;
}

export interface AuditReport {
  id: string;
  framework: string;
  overall_score: number;
  controls_total: number;
  controls_evidenced: number;
  controls_partial: number;
  controls_missing: number;
  critical_gaps?: string;
  evidence_package?: string;
  assessed_at: string;
}

export interface PermissionResponse {
  id: string;
  permission_name: string;
  module: string;
}

export interface RoleResponse {
  id: string;
  role_name: string;
  description?: string;
  permissions: PermissionResponse[];
}

export interface UserResponse {
  id: string;
  email: string;
  display_name: string;
  department?: string;
  tenant_id: string;
  role: RoleResponse;
  is_active: boolean;
  last_login?: string;
  created_at: string;
}

