export type UserRole = 'ENTREPRENEUR' | 'BANK_OFFICER';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  role_display: string;
  phone: string;
  position: string;
}

export interface FinancialData {
  id?: number;
  year: number;
  quarter?: number | null;
  annual_revenue: number;
  net_profit: number;
  current_assets: number;
  current_liabilities: number;
  total_debt: number;
  monthly_credit_payments: number;
  updated_at?: string;
}

export interface Company {
  id: number;
  inn: string;
  ogrn: string;
  kpp: string;
  name: string;
  short_name: string;
  legal_form: 'LLC' | 'IP' | 'JSC';
  legal_form_display: string;
  registration_date: string;
  ceo_name: string;
  okved: string;
  okved_description: string;
  legal_address: string;
  tax_system: string;
  is_active: boolean;
  business_age_years: number;
  financial_reports: FinancialData[];
}

export interface CreditProduct {
  id: number;
  code: string;
  name: string;
  description: string;
  target_purpose: string;
  badge_text: string;
  icon: string;
  min_amount: number | string;
  max_amount: number | string;
  min_term_months: number;
  max_term_months: number;
  base_rate: number | string;
  min_business_age_months: number;
  requires_collateral: boolean;
  requires_surety: boolean;
  required_documents: string[];
  is_active: boolean;
  display_order: number;
}

export type ApplicationStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'VALIDATING'
  | 'ENRICHING'
  | 'SCORING'
  | 'OFFER_READY'
  | 'MANUAL_REVIEW'
  | 'ADDITIONAL_INFO_REQUIRED'
  | 'ACCEPTED'
  | 'REJECTED'
  | 'COMPLETED';

export interface StatusHistoryItem {
  id: number;
  from_status: string;
  to_status: string;
  changed_by: number | null;
  changed_by_name: string;
  reason: string;
  metadata: Record<string, any>;
  created_at: string;
}

export interface VerificationResult {
  id: number;
  source: 'FNS' | 'EGRUL' | 'BKI' | 'SPARK' | 'ARBITRATION';
  source_display: string;
  status: 'PASSED' | 'WARNING' | 'FAILED';
  status_display: string;
  risk_flag_raised: boolean;
  stop_factor_raised: boolean;
  summary: string;
  details: Record<string, any>;
  created_at: string;
}

export interface ScoringFactor {
  category: string;
  name: string;
  impact: string | number;
  type: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  description: string;
}

export interface ScoringResult {
  id: number;
  score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_level_display: string;
  recommendation: 'AUTO_APPROVE' | 'COUNTER_OFFER' | 'MANUAL_REVIEW' | 'REJECT';
  recommendation_display: string;
  factors: ScoringFactor[];
  stop_factors: string[];
  explanation: string;
  calculated_at: string;
}

export interface CreditDecision {
  id: number;
  decision_type: 'APPROVED' | 'COUNTER_OFFER' | 'MANUAL_REVIEW_REQUIRED' | 'ADDITIONAL_INFO_REQUIRED' | 'REJECTED';
  decision_type_display: string;
  is_automated: boolean;
  decided_by: number | null;
  decided_by_name: string;
  approved_amount: number | string;
  approved_term_months: number;
  approved_rate: number | string;
  monthly_payment: number | string;
  rationale: string;
  rejection_reasons: string[];
  underwriter_notes?: string;
  client_response: 'PENDING' | 'ACCEPTED' | 'DECLINED';
  client_response_display: string;
  client_response_at: string | null;
  decided_at: string;
}

export interface DocumentItem {
  id: number;
  doc_type: string;
  doc_type_display: string;
  file_name: string;
  file?: string | null;
  file_size_bytes: number;
  mime_type: string;
  uploaded_by_name: string;
  is_verified: boolean;
  verification_notes?: string;
  uploaded_at: string;
}

export interface ApplicationListItem {
  id: number;
  application_number: string;
  company: number;
  company_name: string;
  company_inn: string;
  product: number;
  product_name: string;
  requested_amount: number | string;
  term_months: number;
  purpose: string;
  status: ApplicationStatus;
  status_display: string;
  applicant: number;
  applicant_name: string;
  scoring_score: number | null;
  risk_level: string | null;
  submitted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationDetail {
  id: number;
  application_number: string;
  applicant: number;
  applicant_name: string;
  company: Company;
  product: CreditProduct;
  requested_amount: number | string;
  term_months: number;
  purpose: string;
  additional_comments: string;
  status: ApplicationStatus;
  status_display: string;
  status_history: StatusHistoryItem[];
  verification_results: VerificationResult[];
  scoring_result: ScoringResult | null;
  decision: CreditDecision | null;
  documents: DocumentItem[];
  submitted_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface InAppNotification {
  id: number;
  application: number | null;
  title: string;
  message: string;
  notification_type: 'INFO' | 'SUCCESS' | 'WARNING' | 'OFFER' | 'DECISION';
  is_read: boolean;
  created_at: string;
}

export interface DemoScenario {
  id: string;
  name: string;
  description: string;
  username: string;
  password: string;
  role: UserRole;
  company: string;
  inn: string;
  expected_outcome: string;
  application_number: string | null;
}
