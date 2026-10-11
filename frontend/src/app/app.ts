import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { catchError, map, of } from 'rxjs';

import { MatchesApi } from './services/matches-api';

import { MatchList } from './components/match-list/match-list'

@Component({
  imports: [MatchList],
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  private readonly api = inject(MatchesApi);

  readonly backendStatus = toSignal(
    this.api.health().pipe(
      map((response) => response.status),
      catchError(() => of('Unreachable')),
    ),
    { initialValue: 'Verification...' },
  );
}