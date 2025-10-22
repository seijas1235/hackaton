import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AgentApiService } from '../../core/agent-api.service';

@Component({
  selector: 'app-agent',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './agent.component.html'
})
export class AgentComponent {
  prompt = '';
  sessionId?: string;
  loading = false;
  messages: { role: 'user' | 'agent'; text: string }[] = [];
  constructor(private api: AgentApiService) {}
  send() {
    const text = this.prompt.trim();
    if (!text) return;
    this.messages.push({ role: 'user', text });
    this.loading = true;
    this.api.agentChat(text, this.sessionId).subscribe({
      next: (res) => {
        this.sessionId = res?.data?.session_id || this.sessionId;
        const reply = res?.data?.message || '(sin respuesta)';
        this.messages.push({ role: 'agent', text: reply });
        this.prompt = ''; this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }
}
