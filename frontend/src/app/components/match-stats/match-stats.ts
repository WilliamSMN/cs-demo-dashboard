import { Component, input, signal, computed, inject } from '@angular/core';
import { DecimalPipe, PercentPipe } from '@angular/common';
import { httpResource } from '@angular/common/http';
import { StatsResponse } from '../../services/matches-api';
import { describeHttpError } from '../../services/http-errors';
import { API_URL } from '../../config';
import { Auth } from '../../services/auth';

type SortKey = 'kills' | 'deaths' | 'assists' | 'adr' | 'hs_pct';

@Component({
  imports: [DecimalPipe, PercentPipe],
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

  protected readonly sortKey = signal<SortKey>('kills');

  protected readonly teamGroups = computed(() => {
    const key = this.sortKey();
    const teams = this.stats.value()?.teams ?? [];

    return teams.map((team) => ({
      ...team,
      players: [...team.players].sort((a, b) => b[key] - a[key]),
    }));
  });

  protected readonly usersTeam = computed(() => {
    const userSteamId = this.auth.userSteamId();
    if (!userSteamId) return undefined;

    // Trouve directement l'équipe qui contient le joueur
    const team = this.teamGroups().find((t) => t.players.some((p) => p.steamid === userSteamId));
    return team?.name;
  });

  protected readonly winningTeam = computed(() => {
    const teams = this.teamGroups();
    if (teams.length === 0) return undefined;

    return teams.reduce((maxTeam, currentTeam) =>
      currentTeam.score > maxTeam.score ? currentTeam : maxTeam,
    ).name;
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
