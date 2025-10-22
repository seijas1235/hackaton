import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AgentApiService } from '../../core/agent-api.service';

@Component({
  selector: 'app-actions',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './actions.component.html'
})
export class ActionsComponent implements OnInit {
  rows: any[] = [];
  loading = false;
  constructor(private api: AgentApiService) {}
  ngOnInit(): void {
    this.loading = true;
    this.api.listActions(50).subscribe({
      next: (res) => { this.rows = res.data || []; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }
}
