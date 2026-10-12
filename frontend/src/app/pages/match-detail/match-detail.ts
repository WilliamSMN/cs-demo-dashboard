import { Component, input, inject, computed } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatchesStore } from '../../services/matches-store';

import { MatchMeta } from '../../services/matches-api';

type MatchView =
  | { kind: 'loading' }
  | { kind: 'error' }
  | { kind: 'notFound' }
  | { kind: 'found'; match: MatchMeta };

@Component({
  imports: [RouterLink],
  selector: 'app-match-detail',
  styleUrl: './match-detail.scss',
  templateUrl: './match-detail.html',
})
export class MatchDetail {
  readonly id = input.required<string>();
  protected readonly store = inject(MatchesStore);
  protected readonly view = computed<MatchView>(() => {
    const state = this.store.matchState();

    if (state.kind !== 'ready') {
      return state;
    }

    const match = state.matches.find((m) => m.id === this.id());
    return match ? { kind: 'found', match } : { kind: 'notFound' };
  });
}
