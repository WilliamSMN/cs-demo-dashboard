import { Component, input, signal, computed, inject } from '@angular/core';
import { httpResource } from '@angular/common/http';
import { StatsResponse, SteamProfile } from '../../services/matches-api';
import { describeHttpError } from '../../services/http-errors';
import { API_URL } from '../../config';
import { Auth } from '../../services/auth';
import { TradesTable } from '../trades-table/trades-table';
import { ScoreboardTable } from '../scoreboard-table/scoreboard-table';
import { UtilityTable } from '../utility-table/utility-table';
import { ClutchTable } from '../clutch-table/clutch-table';
import { DecimalPipe, PercentPipe } from '@angular/common';

type PrimaryTab = 'general' | 'report';
type StatsTab = 'scoreboard' | 'utility' | 'trades' | 'clutch';

@Component({
  imports: [DecimalPipe, PercentPipe, TradesTable, ScoreboardTable, UtilityTable, ClutchTable],
  selector: 'app-match-stats',
  styleUrl: './match-stats.scss',
  templateUrl: './match-stats.html',
})
export class MatchStats {
  readonly matchId = input.required<string>();
  readonly mapName = input<string>('Unknown map');
  protected readonly stats = httpResource<StatsResponse>(
    () => `${API_URL}/matches/${this.matchId()}/stats`,
  );
  protected readonly auth = inject(Auth);

  protected readonly profile = httpResource<SteamProfile>(() =>
    this.auth.userSteamId() ? `${API_URL}/users/me/steam-profile` : undefined,
  );

  protected readonly activeTab = signal<PrimaryTab>('general');
  protected readonly statsTab = signal<StatsTab>('scoreboard');

  protected readonly statsTabs: { key: StatsTab; label: string }[] = [
    { key: 'scoreboard', label: 'Scoreboard' },
    { key: 'utility', label: 'Utility' },
    { key: 'trades', label: 'Trades' },
    { key: 'clutch', label: 'Clutch' },
  ];

  protected readonly usersTeam = computed(() => {
    const userSteamId = this.auth.userSteamId();
    if (!userSteamId) return undefined;

    // Trouve directement l'équipe qui contient le joueur
    const team = (this.stats.value()?.teams ?? []).find((t) =>
      t.players.some((p) => p.steamid === userSteamId),
    );
    return team?.name;
  });

  protected readonly userPlayer = computed(() => {
    const steamId = this.auth.userSteamId();
    if (!steamId) return undefined;

    return (this.stats.value()?.teams ?? [])
      .flatMap((team) => team.players)
      .find((player) => player.steamid === steamId);
  });

  protected readonly userTeam = computed(() => {
    const player = this.userPlayer();
    if (!player) return undefined;

    return (this.stats.value()?.teams ?? []).find((team) =>
      team.players.some((p) => p.steamid === player.steamid),
    );
  });

  protected readonly matchWon = computed(() => {
    const team = this.userTeam();
    if (!team) return false;

    return team.score === Math.max(...(this.stats.value()?.teams ?? []).map((t) => t.score));
  });

  protected readonly matchLost = computed(() => {
    const team = this.userTeam();
    if (!team) return false;

    return team.score < Math.max(...(this.stats.value()?.teams ?? []).map((t) => t.score));
  });

  protected readonly errorMessage = computed(() => {
    const err = this.stats.error();
    const cause = err instanceof Error && err.cause ? err.cause : err;
    return describeHttpError(cause);
  });
}
