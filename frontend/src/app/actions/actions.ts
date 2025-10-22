import { Component, OnInit, inject } from '@angular/core';
import { DatePipe, TitleCasePipe } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatBadgeModule } from '@angular/material/badge';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatPaginatorModule } from '@angular/material/paginator';
import { AgentApiService, AgentAction } from '../core/agent-api.service';

@Component({
  selector: 'app-actions',
  imports: [DatePipe, TitleCasePipe, MatCardModule, MatButtonModule, MatIconModule, MatTableModule, MatChipsModule, MatProgressSpinnerModule, MatBadgeModule, MatTooltipModule, MatPaginatorModule],
  templateUrl: './actions.html',
  styleUrl: './actions.scss'
})
export class ActionsComponent implements OnInit {
  private agentApiService = inject(AgentApiService);

  actions: AgentAction[] = [];
  executions: any[] = [];
  loading = true;
  total = 0;
  pageSize = 10;
  currentPage = 0;
  displayedColumns: string[] = ['name', 'type', 'description', 'actions'];
  executionColumns: string[] = ['id', 'action', 'status', 'startTime', 'duration'];

  ngOnInit() {
    this.loadActions();
  }

  private loadActions() {
    this.loading = true;
    this.agentApiService.listActions(this.pageSize, this.currentPage * this.pageSize).subscribe({
      next: (response) => {
        this.actions = response.actions;
        this.total = response.total;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading actions:', error);
        this.loading = false;
      }
    });
  }

  onPageChange(event: any) {
    this.currentPage = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadActions();
  }

  createAction() {
    // TODO: Implement create action dialog
    console.log('Create action');
  }

  editAction(action: AgentAction) {
    // TODO: Implement edit action dialog
    console.log('Edit action:', action);
  }

  deleteAction(action: AgentAction) {
    // TODO: Implement delete confirmation
    console.log('Delete action:', action);
  }

  executeAction(action: AgentAction) {
    // TODO: Implement action execution dialog
    console.log('Execute action:', action);
  }

  getTypeColor(type: string): string {
    switch (type) {
      case 'api_call': return 'primary';
      case 'database_query': return 'accent';
      case 'file_operation': return 'warn';
      default: return '';
    }
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'completed': return 'primary';
      case 'running': return 'accent';
      case 'failed': return 'warn';
      default: return '';
    }
  }

  formatLastExecuted(dateString?: string): string {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  }

  calculateDuration(execution: any): string {
    if (!execution.endTime) return 'Running...';
    const start = new Date(execution.startTime);
    const end = new Date(execution.endTime);
    const duration = end.getTime() - start.getTime();
    return `${Math.round(duration / 1000)}s`;
  }
}
