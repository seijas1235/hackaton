import { Component, OnInit, inject } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'app-callback',
  imports: [MatProgressSpinnerModule],
  templateUrl: './callback.html',
  styleUrl: './callback.scss'
})
export class CallbackComponent implements OnInit {
  private authService = inject(AuthService);

  ngOnInit(): void {
    // Handle the authentication callback
    this.authService.handleRedirectCallback();
  }
}
