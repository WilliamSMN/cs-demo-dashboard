import { Component, inject  } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { catchError, map, of } from 'rxjs';
import { MatchesApi, MatchMeta } from '../../services/matches-api';

type MatchesState =
  | { kind: 'loading' }
  | { kind: 'error' }
  | { kind: 'ready'; matches: MatchMeta[] };

@Component({
  selector: 'app-match-list',
  styleUrl: './match-list.scss',
  templateUrl: './match-list.html',
})
export class MatchList {
  private readonly api = inject(MatchesApi);

  readonly state = toSignal(
    this.api.list().pipe(
      map((matches): MatchesState => ({ kind: 'ready', matches })),
      catchError(() => of<MatchesState>({ kind: 'error' })),
    ),
    { initialValue: { kind: 'loading' } },
  );
}
