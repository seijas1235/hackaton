import { Component, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'app-login',
  imports: [MatCardModule, MatButtonModule, MatIconModule],
  templateUrl: './login.html',
  styleUrl: './login.scss'
})
export class LoginComponent {
  private authService = inject(AuthService);

  /**
   * Initiate login flow by redirecting to Cognito Hosted UI
   */
  login(): void {
    this.authService.login();
  }
}
