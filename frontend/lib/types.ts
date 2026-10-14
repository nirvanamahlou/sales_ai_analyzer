export interface CallAnalysis {
  id: string;
  crm_activity_id: string;
  date: string;
  customer_phone: string | null;
  lead_score: number;
  agent_performance: string | null;
  strengths: string[];
  weaknesses: string[];
}
