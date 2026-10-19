import { Component, input } from '@angular/core';
import { httpResource } from '@angular/common/http';
import { PercentPipe } from '@angular/common';
import { ClutchResponse } from '../../services/matches-api';
import { describeHttpError } from '../../services/http-errors';
import { API_URL } from '../../config';
import { sumBy, ratio } from '../../utils/stats';

@Component({
  imports: [PercentPipe],
  selector: 'app-clutch-table',
  styleUrl: './clutch-table.scss',
  templateUrl: './clutch-table.html',
})
export class ClutchTable {
  readonly matchId = input.required<string>();
  readonly userSteamId = input<string | undefined>();
  readonly usersTeam = input<string | undefined>();

  protected readonly clutch = httpResource<ClutchResponse>(
    () => `${API_URL}/matches/${this.matchId()}/clutch`,
  );

  protected readonly sumBy = sumBy;
  protected readonly ratio = ratio;
}
