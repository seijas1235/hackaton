import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AgentApiService } from '../../core/agent-api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html'
})
export class DashboardComponent implements OnInit {
  loading = true;
  kpis: any = {};
  constructor(private api: AgentApiService) {}
  ngOnInit(): void {
    this.api.getKPIs('last_30d').subscribe({
      next: (res) => { this.kpis = res.data; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }
}
