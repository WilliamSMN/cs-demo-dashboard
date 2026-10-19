import { Component, input } from '@angular/core';
import { httpResource } from '@angular/common/http';
import { TradesResponse } from '../../services/matches-api';
import { sumBy } from '../../utils/stats';
import { API_URL } from '../../config';

@Component({
  imports: [],
  selector: 'app-trades-table',
  styleUrl: './trades-table.scss',
  templateUrl: './trades-table.html',
})
export class TradesTable {
  readonly matchId = input.required<string>();
  protected readonly trades = httpResource<TradesResponse>(
    () => `${API_URL}/matches/${this.matchId()}/trades`,
  );
  readonly userSteamId = input<string | undefined>();
  readonly usersTeam = input<string | undefined>();

  protected readonly sumBy = sumBy;
}
