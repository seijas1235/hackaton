import { Component, OnInit, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { AgentApiService } from '../core/agent-api.service';

export interface Agent {
  id: string;
  name: string;
  model: string;
  description: string;
  status: 'active' | 'inactive';
  lastUsed?: string;
}

@Component({
  selector: 'app-agent',
  imports: [MatCardModule, MatButtonModule, MatIconModule, MatTableModule, MatProgressSpinnerModule, MatTooltipModule],
  templateUrl: './agent.html',
  styleUrl: './agent.scss'
})
export class AgentComponent implements OnInit {
  private agentApiService = inject(AgentApiService);

  agents: Agent[] = [];
  loading = true;
  displayedColumns: string[] = ['name', 'model', 'description', 'actions'];

  ngOnInit() {
    this.loadAgents();
  }

  private loadAgents() {
    this.loading = true;
    // Mock data for now - replace with actual API call when backend is ready
    setTimeout(() => {
      this.agents = [
        {
          id: '1',
          name: 'Sales Assistant',
          model: 'GPT-4',
          description: 'Helps with sales analytics and customer insights',
          status: 'active',
          lastUsed: '2024-01-15'
        },
        {
          id: '2',
          name: 'Financial Advisor',
          model: 'GPT-4',
          description: 'Provides financial analysis and cash flow projections',
          status: 'active',
          lastUsed: '2024-01-14'
        }
      ];
      this.loading = false;
    }, 1000);
  }

  createAgent() {
    // TODO: Implement create agent dialog
    console.log('Create agent');
  }

  editAgent(agent: Agent) {
    // TODO: Implement edit agent dialog
    console.log('Edit agent:', agent);
  }

  deleteAgent(agent: Agent) {
    // TODO: Implement delete confirmation
    console.log('Delete agent:', agent);
  }

  chatWithAgent(agent: Agent) {
    // Navigate to chat interface
    console.log('Chat with agent:', agent);
  }
}
