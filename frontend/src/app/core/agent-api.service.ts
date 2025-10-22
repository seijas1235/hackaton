import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AgentApiService {
  private base = environment.apiBaseUrl;
  constructor(private http: HttpClient) {}

  getKPIs(period = 'last_30d') {
    const params = new HttpParams().set('period', period);
    return this.http.get<any>(`${this.base}/agent/tools/kpis`, { params });
  }
  getCashflow(horizon = 30) {
    const params = new HttpParams().set('horizon', horizon);
    return this.http.get<any>(`${this.base}/agent/tools/cashflow`, { params });
  }
  getAnomalies(period = 'last_60d') {
    const params = new HttpParams().set('period', period);
    return this.http.get<any>(`${this.base}/agent/tools/anomalies`, { params });
  }
  createCollectionReminder(payload: { customer_id: number; invoice_id?: number; remind_date: string }) {
    return this.http.post<any>(`${this.base}/agent/actions/collection-reminder`, payload);
  }
  listActions(limit = 50) {
    const params = new HttpParams().set('limit', limit);
    return this.http.get<any>(`${this.base}/agent/actions`, { params });
  }
  agentChat(prompt: string, session_id?: string) {
    return this.http.post<any>(`${this.base}/agent/chat`, { prompt, session_id });
  }
}