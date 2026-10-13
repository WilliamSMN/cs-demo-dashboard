import { Component, input, signal, computed } from '@angular/core';
import { DecimalPipe, PercentPipe } from '@angular/common';
import { httpResource } from '@angular/common/http';
import { StatsResponse } from '../../services/matches-api';
import { describeHttpError } from '../../services/http-errors';
import { API_URL } from '../../config';

type SortKey = 'kills' | 'deaths' | 'assists' | 'adr' | 'hs_pct';

@Component({
  imports: [DecimalPipe, PercentPipe],
  selector: 'app-match-stats',
  styleUrl: './match-stats.scss',
  templateUrl: './match-stats.html',
})
export class MatchStats {
  readonly matchId = input.required<string>();
  protected readonly stats = httpResource<StatsResponse>(
    () => `${API_URL}/matches/${this.matchId()}/stats`,
  );

  protected readonly sortKey = signal<SortKey>('kills');
  protected readonly sortedPlayers = computed(() => {
    const key = this.sortKey();
    const players = this.stats.value()?.players ?? [];
    return [...players].sort((a, b) => b[key] - a[key]); // descending
  });
  protected readonly errorMessage = computed(() => {
    const err = this.stats.error();
    const cause = err instanceof Error && err.cause ? err.cause : err;
    return describeHttpError(cause);
  });
}
