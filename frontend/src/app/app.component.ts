import { Component, computed } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from './core/auth.service';

@Component({
  standalone: true,
  selector: 'app-root',
  imports: [CommonModule, RouterOutlet, RouterLink],
  templateUrl: './app.component.html'
})
export class AppComponent {
  constructor(public auth: AuthService) {}
  // SRP: AppComponent solo orquesta la vista raíz.
  readonly isAuth = computed(() => !!this.auth.getAccessToken());
  login()  { this.auth.login(); }
  logout() { this.auth.logout(); }
}
