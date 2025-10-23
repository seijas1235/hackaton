import 'zone.js';
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';
import { AuthService } from './app/core/auth.service';
import { Router } from '@angular/router';

bootstrapApplication(AppComponent, appConfig).then(ref => {
  // Maneja el hash de Cognito tras el login (Implicit flow)
  const auth = ref.injector.get(AuthService);
  const router = ref.injector.get(Router);
  
  // Si hay hash con tokens, procesarlos y redirigir a dashboard
  if (typeof window !== 'undefined' && window.location.hash.includes('access_token')) {
    auth.handleRedirectCallback();
    router.navigate(['/dashboard']);
  }
}).catch(console.error);
