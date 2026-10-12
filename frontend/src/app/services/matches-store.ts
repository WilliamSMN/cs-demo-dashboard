import { Injectable, inject, signal, effect } from '@angular/core';
import { MatchesApi, MatchMeta } from './matches-api';

const POLL_INTERVAL_MS = 2000;

export type MatchesState =
  { kind: 'loading' } | { kind: 'error' } | { kind: 'ready'; matches: MatchMeta[] };

@Injectable({ providedIn: 'root' })
export class MatchesStore {
  private readonly _matches = signal<MatchMeta[]>([]);
  private readonly api = inject(MatchesApi);
  readonly matchState = signal<MatchesState>({ kind: 'loading' });

  add(match: MatchMeta) {
    this._matches.update((matches) => [...matches, match]);
  }

  refresh() {
    this.api.list().subscribe({
      next: (matches) => {
        this._matches.set(matches);
        this.matchState.set({ kind: 'ready', matches: matches });
      },
      error: () => {
        this.matchState.set({ kind: 'error' });
      },
    });
  }

  constructor() {
    this.refresh();
    effect((onCleanup) => {
      const s = this.matchState();
      if (s.kind == 'ready') {
        const updatedMatchesStatus = s.matches.some((m) => m.status === 'processing');
        if (updatedMatchesStatus) {
          const timer = setTimeout(() => this.refresh(), POLL_INTERVAL_MS);
          onCleanup(() => clearTimeout(timer));
        }
      }
    });
  }
}
