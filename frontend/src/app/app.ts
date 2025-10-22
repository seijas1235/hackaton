import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { AsyncPipe } from '@angular/common';
import { Observable, map, shareReplay } from 'rxjs';
import { AuthService } from './core/auth.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, MatToolbarModule, MatButtonModule, MatSidenavModule, MatIconModule, MatListModule, AsyncPipe],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly title = signal('Hackathon App');
  private authService = inject(AuthService);
  private breakpointObserver = inject(BreakpointObserver);

  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches),
      shareReplay()
    );

  ngOnInit(): void {
    // Initialize authentication on app startup
    this.authService.initializeAuth();
  }

  get isAuthenticated$() {
    return this.authService.isAuthenticated$;
  }

  get user$() {
    return this.authService.user$;
  }

  logout(): void {
    this.authService.logout();
  }
}
