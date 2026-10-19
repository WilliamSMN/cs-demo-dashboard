import { Component, input, signal, computed } from '@angular/core';
import { DecimalPipe, PercentPipe } from '@angular/common';
import { TeamStats } from '../../services/matches-api';
import { sumBy } from '../../utils/stats';

type SortKey = 'kills' | 'deaths' | 'assists' | 'adr' | 'hs_pct';

@Component({
  imports: [DecimalPipe, PercentPipe],
  selector: 'app-scoreboard-table',
  styleUrl: './scoreboard-table.scss',
  templateUrl: './scoreboard-table.html',
})
export class ScoreboardTable {
  readonly teams = input.required<TeamStats[]>();
  readonly userSteamId = input<string | undefined>();
  readonly usersTeam = input<string | undefined>();

  protected readonly sortKey = signal<SortKey>('kills');

  protected readonly teamGroups = computed(() => {
    const key = this.sortKey();
    const teams = this.teams() ?? [];

    return teams.map((team) => ({
      ...team,
      players: [...team.players].sort((a, b) => b[key] - a[key]),
    }));
  });

  protected readonly winningTeam = computed(() => {
    const teams = this.teamGroups() ?? [];
    if (teams.length === 0) return undefined;

    return teams.reduce((maxTeam, currentTeam) =>
      currentTeam.score > maxTeam.score ? currentTeam : maxTeam,
    ).name;
  });

  protected readonly sumBy = sumBy;
}
