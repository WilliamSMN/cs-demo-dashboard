import { Service, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { API_URL } from '../config';
import { describeHttpError } from './http-errors';

type AuthState =
  | { kind: 'signedOut' }
  | { kind: 'loading' }
  | { kind: 'error'; message: string }
  | { kind: 'signedIn'; steamid: string };

@Service()
export class Auth {
  private readonly http = inject(HttpClient);
  readonly authState = signal<AuthState>({ kind: 'signedOut' });
  readonly loginUrl = `${API_URL}/auth/steam/login`;

  async load(): Promise<void> {
    try {
      this.authState.set({ kind: 'loading' });
      const me = await firstValueFrom(this.http.get<{ steamid: string }>(`${API_URL}/auth/me`));
      this.authState.set({ kind: 'signedIn', steamid: me.steamid });
    } catch (err) {
      if (err instanceof HttpErrorResponse && err.status === 401) {
        this.authState.set({ kind: 'signedOut' });
      } else {
        this.authState.set({ kind: 'error', message: describeHttpError(err) });
      }
    }
  }

  async logout(): Promise<void> {
    try {
      await firstValueFrom(this.http.post<void>(`${API_URL}/auth/logout`, null));
    } catch (err) {
      this.authState.set({ kind: 'error', message: describeHttpError(err) });
    } finally {
      window.location.assign('/');
    }
  }
}
