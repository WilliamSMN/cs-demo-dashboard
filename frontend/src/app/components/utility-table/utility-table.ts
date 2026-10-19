import { Component, input } from '@angular/core';
import { httpResource } from '@angular/common/http';
import { UtilityResponse } from '../../services/matches-api';
import { describeHttpError } from '../../services/http-errors';
import { API_URL } from '../../config';
import { sumBy } from '../../utils/stats';

@Component({
  imports: [],
  selector: 'app-utility-table',
  styleUrl: './utility-table.scss',
  templateUrl: './utility-table.html',
})
export class UtilityTable {
  readonly matchId = input.required<string>();
  readonly userSteamId = input<string | undefined>();
  readonly usersTeam = input<string | undefined>();

  protected readonly utility = httpResource<UtilityResponse>(
    () => `${API_URL}/matches/${this.matchId()}/utility`,
  );

  protected readonly sumBy = sumBy;
}
