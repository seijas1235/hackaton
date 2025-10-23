import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../shared/api.service';

@Component({
  standalone: true,
  selector: 'app-agent',
  imports: [CommonModule, FormsModule],
  template: `
    <h2>Agent</h2>
    <textarea [(ngModel)]="prompt" rows="4" style="width:100%" placeholder="Ej: Haz un forecast de caja a 30 días"></textarea>
    <div style="margin-top:8px">
      <button (click)="ask()" [disabled]="loading || !prompt">Enviar</button>
    </div>
    <div *ngIf="error" style="color:#b00">Error: {{error}}</div>
    <pre *ngIf="answer" style="background:#111;color:#0f0;padding:12px;border-radius:12px">{{answer}}</pre>
  `
})
export class AgentComponent {
  prompt = ''; answer = ''; loading = false; error = '';
  constructor(private api: ApiService) {}
  ask(){
    this.loading = true; this.error = ''; this.answer = '';
    this.api.agentChat({ prompt: this.prompt, session_id: null }).subscribe({
      next: r => { this.answer = r?.text || JSON.stringify(r,null,2); this.loading = false; },
      error: e => { this.error = e?.message || 'Error'; this.loading = false; }
    });
  }
}
