import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../core/auth.service';

@Component({
  standalone: true,
  selector: 'app-login',
  imports: [CommonModule],
  template: `
    <div style="display:flex;align-items:center;justify-content:center;min-height:80vh">
      <div style="text-align:center;max-width:400px;padding:24px;border:1px solid #eee;border-radius:12px">
        <h1>CFO Agent</h1>
        <p style="color:#666;margin:16px 0">Sistema de análisis financiero con IA</p>
        <button 
          (click)="login()" 
          style="padding:12px 32px;font-size:16px;background:#0066cc;color:white;border:none;border-radius:8px;cursor:pointer">
          Iniciar sesión con Cognito
        </button>
        <p style="color:#999;font-size:12px;margin-top:24px">
          Serás redirigido a AWS Cognito para autenticarte
        </p>
      </div>
    </div>
  `
})
export class LoginComponent {
  constructor(private auth: AuthService) {}
  login() { this.auth.login(); }
}
