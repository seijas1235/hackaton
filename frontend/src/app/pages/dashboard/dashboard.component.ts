import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../shared/api.service';

@Component({
  standalone: true,
  selector: 'app-dashboard',
  imports: [CommonModule],
  template: `
    <h2>Dashboard</h2>
    <button (click)="load()" [disabled]="loading">Refrescar</button>
    <div *ngIf="error" style="color:#b00">Error: {{error}}</div>
    <div *ngIf="!loading && data" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:12px">
      <div style="border:1px solid #eee;padding:12px;border-radius:12px"><strong>Ventas 30d:</strong><div>{{data.sales_30d}}</div></div>
      <div style="border:1px solid #eee;padding:12px;border-radius:12px"><strong>Margen 30d:</strong><div>{{data.margin_30d}}</div></div>
      <div style="border:1px solid #eee;padding:12px;border-radius:12px"><strong>AR total:</strong><div>{{data.ar_total}}</div></div>
      <div style="border:1px solid #eee;padding:12px;border-radius:12px"><strong>AR &gt; 60d:</strong><div>{{data.ar_over_60d}}</div></div>
    </div>
  `
})
export class DashboardComponent implements OnInit {
  data: any; loading = false; error = '';
  constructor(private api: ApiService) {}
  ngOnInit(){ this.load(); }
  load(){
    this.loading = true; this.error = '';
    this.api.getKPIs().subscribe({
      next: d => { this.data = d; this.loading = false; },
      error: e => { 
        console.error('Error completo:', e);
        console.error('Status:', e?.status);
        console.error('Body:', e?.error);
        this.error = e?.error?.message || e?.message || `Error ${e?.status}: ${e?.statusText}`; 
        this.loading = false; 
      }
    });
  }
}
