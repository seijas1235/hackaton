import { Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatGridListModule } from '@angular/material/grid-list';
import { AgentApiService } from '../core/agent-api.service';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, MatCardModule, MatButtonModule, MatIconModule, MatGridListModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class DashboardComponent implements OnInit {
  private agentApiService = inject(AgentApiService);
  private authService = inject(AuthService);

  metrics = {
    totalAgents: 0,
    totalChats: 0,
    totalActions: 0,
    activeExecutions: 0
  };

  ngOnInit() {
    this.loadDashboardMetrics();
  }

  private loadDashboardMetrics() {
    this.agentApiService.getDashboardMetrics().subscribe({
      next: (data) => {
        this.metrics = data;
      },
      error: (error) => {
        console.error('Error loading dashboard metrics:', error);
      }
    });
  }

  getCurrentUser() {
    return this.authService.getCurrentUser();
  }
}
