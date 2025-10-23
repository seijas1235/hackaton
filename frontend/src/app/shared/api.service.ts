import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { KPIResponse, CashflowResponse, AgentChatRequest, AgentChatResponse } from './models';

/** ApiService — SRP: acceso a endpoints del backend */
@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly base = environment.apiBaseUrl;
  constructor(private http: HttpClient) {}
  getKPIs(period = 'last_30d') {
    return this.http.get<KPIResponse>(`${this.base}/agent/tools/kpis?period=${encodeURIComponent(period)}`);
  }
  getCashflow(horizon = 30) {
    return this.http.get<CashflowResponse>(`${this.base}/agent/tools/cashflow?horizon=${horizon}`);
  }
  agentChat(body: AgentChatRequest) {
    return this.http.post<AgentChatResponse>(`${this.base}/agent/chat`, body);
  }
}