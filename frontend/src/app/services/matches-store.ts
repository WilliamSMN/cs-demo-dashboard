import { Injectable, inject, signal } from '@angular/core';
import { MatchesApi, MatchMeta } from './matches-api';


export type MatchesState =
  | { kind: 'loading' }
  | { kind: 'error' }
  | { kind: 'ready'; matches: MatchMeta[] };

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
            error: () => { this.matchState.set({ kind: 'error' }) },
        });
    }

    constructor() {
        this.refresh();
    }
}
