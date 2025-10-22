import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private accessTokenKey = 'access_token';
  private idTokenKey = 'id_token';

  login(): void {
    const url = new URL(`https://${environment.cognitoDomain}/oauth2/authorize`);
    url.searchParams.set('client_id', environment.cognitoClientId);
    url.searchParams.set('response_type', 'token');
    url.searchParams.set('scope', 'openid profile email agent/actions');
    url.searchParams.set('redirect_uri', environment.cognitoRedirectUri);
    window.location.href = url.toString();
  }

  handleRedirectCallback(): void {
    if (window.location.hash.startsWith('#')) {
      const params = new URLSearchParams(window.location.hash.substring(1));
      const access = params.get('access_token');
      const id = params.get('id_token');
      if (access) localStorage.setItem(this.accessTokenKey, access);
      if (id) localStorage.setItem(this.idTokenKey, id);
      history.replaceState(null, '', window.location.pathname);
    }
  }

  getAccessToken(): string | null { return localStorage.getItem(this.accessTokenKey); }
  isAuthenticated(): boolean { return !!this.getAccessToken(); }

  logout(): void {
    localStorage.removeItem(this.accessTokenKey);
    localStorage.removeItem(this.idTokenKey);
    const url = new URL(`https://${environment.cognitoDomain}/logout`);
    url.searchParams.set('client_id', environment.cognitoClientId);
    url.searchParams.set('logout_uri', environment.cognitoRedirectUri);
    window.location.href = url.toString();
  }
}