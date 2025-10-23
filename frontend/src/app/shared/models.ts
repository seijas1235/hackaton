export interface KPIResponse {
  sales_30d: number;
  margin_30d: number;
  ar_total: number;
  ar_over_60d: number;
}
export interface CashflowPoint { date: string; amount: number; }
export interface CashflowResponse { horizon_days: number; forecast: CashflowPoint[]; }
export interface AgentChatRequest { prompt: string; session_id?: string | null; }
export interface AgentChatResponse { text?: string; session_id?: string | null; [k: string]: any; }