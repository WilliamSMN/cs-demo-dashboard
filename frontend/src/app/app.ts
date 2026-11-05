import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { catchError, map, of } from 'rxjs';

import { MatchesApi } from './services/matches-api';
import { AuthBar } from './components/auth-bar/auth-bar';
import { Auth } from './services/auth';

@Component({
  imports: [RouterOutlet, RouterLink, AuthBar, RouterLinkActive],
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  private readonly api = inject(MatchesApi);
  private readonly auth = inject(Auth);

  readonly backendStatus = toSignal(
    this.api.health().pipe(
      map((response) => response.status),
      catchError(() => of('Unreachable')),
    ),
    { initialValue: 'Verification...' },
  );
}
