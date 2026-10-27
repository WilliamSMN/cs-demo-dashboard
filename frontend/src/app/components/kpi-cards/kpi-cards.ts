import { Component, computed, input } from '@angular/core';
import { OpeningDuel, PlayerReportSummary } from '../../services/report-api';

@Component({
  imports: [],
  selector: 'app-kpi-cards',
  styleUrl: './kpi-cards.scss',
  templateUrl: './kpi-cards.html',
})
export class KpiCards {
  readonly summary = input.required<PlayerReportSummary>();
  readonly duels = input.required<OpeningDuel[]>();

  protected readonly cards = computed(() => {
    const s = this.summary();
    const won = this.duels().filter((d) => d.won).length;
    const total = this.duels().length;
    return [
      { label: 'RATING', value: s.rating === null ? '-' : s.rating.toFixed(2), sub: `HLTV 2.0 (approx.)` },
      { label: 'ADR', value: s.adr.toFixed(1), sub: `${s.damage} damage` },
      { label: 'KAST', value: s.kast === null ? '-' : `${Math.round(s.kast * 100)}%`, sub: s.kast === null ? '' : `${Math.round(s.kast * s.rounds)} / ${s.rounds} rounds` },
      { label: 'K/D', value: s.kills === null ? '-' : (s.kills/Math.max(s.deaths, 1)).toFixed(2), sub: `${s.kills} / ${s.deaths} / ${s.assists}` },
      { label: 'HS %', value: s.hs_pct === null ? '-' : `${(100*s.hs_pct).toFixed(1)}%`, sub: `${Math.round(s.kills*s.hs_pct)} / ${s.kills} kills` },
      { label: 'OPENING DUELS', value: `${won} - ${total - won}`, sub: total === 0 ? '-' : `${Math.round(100*(won/total))}% won` }
    ];
  });
}
