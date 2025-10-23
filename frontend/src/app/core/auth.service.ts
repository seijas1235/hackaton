import { Injectable, PLATFORM_ID, inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { environment } from '../../environments/environment';

/**
 * AuthService — SRP: gestionar Hosted UI (Implicit), tokens y logout.
 * SOLID: Dependencias mínimas y API clara (login, logout, getAccessToken).
 * Compatible con SSR usando isPlatformBrowser.
 */
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly accessTokenKey = 'access_token';
  private readonly idTokenKey = 'id_token';
  private readonly platformId = inject(PLATFORM_ID);
  private readonly isBrowser = isPlatformBrowser(this.platformId);

  login(): void {
    if (!this.isBrowser) return;
    const url = new URL(`https://${environment.cognitoDomain}/login`);
    url.searchParams.set('client_id', environment.cognitoClientId);
    url.searchParams.set('redirect_uri', environment.cognitoRedirectUri);
    url.searchParams.set('response_type', 'token');
    url.searchParams.set('scope', 'email openid phone');
    window.location.href = url.toString();
  }

  handleRedirectCallback(): void {
    if (!this.isBrowser) return;
    if (window.location.hash.startsWith('#')) {
      const params = new URLSearchParams(window.location.hash.substring(1));
      const access = params.get('access_token');
      const id = params.get('id_token');
      if (access) localStorage.setItem(this.accessTokenKey, access);
      if (id) localStorage.setItem(this.idTokenKey, id);
      history.replaceState(null, '', window.location.pathname);
    }
  }

  getAccessToken(): string | null {
    if (!this.isBrowser) return null;
    return localStorage.getItem(this.accessTokenKey);
  }

  isAuthenticated(): boolean { return !!this.getAccessToken(); }

  logout(): void {
    if (!this.isBrowser) return;
    localStorage.removeItem(this.accessTokenKey);
    localStorage.removeItem(this.idTokenKey);
    const url = new URL(`https://${environment.cognitoDomain}/logout`);
    url.searchParams.set('client_id', environment.cognitoClientId);
    url.searchParams.set('logout_uri', environment.cognitoRedirectUri);
    window.location.href = url.toString();
  }
}