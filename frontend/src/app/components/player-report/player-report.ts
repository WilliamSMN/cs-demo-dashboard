import { Component, computed, input } from '@angular/core';
import { ExtrasResponse, KillTimingResponse, OpeningDuelsResponse, PlayerReportSummary, PositionsResponse, ProfileResponse, RoundImpactResponse, WeaponsResponse } from '../../services/report-api';
import { API_URL } from '../../config';
import { httpResource } from '@angular/common/http';
import { describeHttpError } from '../../services/http-errors';
import { KpiCards } from '../kpi-cards/kpi-cards';
import { RoundImpactChart } from '../round-impact-chart/round-impact-chart';
import { ProfileRadar } from '../profile-radar/profile-radar';
import { KillMap } from '../kill-map/kill-map';
import { DuelsCard } from '../duels-card/duels-card';
import { UtilityCard } from '../utility-card/utility-card';
import { TimingHistogram } from '../timing-histogram/timing-histogram';
import { WeaponsTable } from '../weapons-table/weapons-table';
import { OpponentsTable } from '../opponents-table/opponents-table';

@Component({
  imports: [KpiCards, RoundImpactChart, ProfileRadar, KillMap, DuelsCard, UtilityCard, TimingHistogram, WeaponsTable, OpponentsTable],
  selector: 'app-player-report',
  styleUrl: './player-report.scss',
  templateUrl: './player-report.html',
})
export class PlayerReport {
  readonly matchId = input.required<string>();

  private report<T>(name: string) {
    return httpResource<T>(() => `${API_URL}/matches/${this.matchId()}/report/${name}`);
  }

  protected readonly summary = this.report<PlayerReportSummary>('summary');
  protected readonly rounds = this.report<RoundImpactResponse>('rounds');
  protected readonly timing = this.report<KillTimingResponse>('timing');
  protected readonly opening = this.report<OpeningDuelsResponse>('opening');
  protected readonly extras = this.report<ExtrasResponse>('extras');
  protected readonly weapons = this.report<WeaponsResponse>('weapons');
  protected readonly positions = this.report<PositionsResponse>('positions');
  protected readonly profile = this.report<ProfileResponse>('profile');

  protected readonly errorMessage = computed(() => {
    const err = this.summary.error();
    const cause = err instanceof Error && err.cause ? err.cause : err;
    return describeHttpError(cause);
  });
}
