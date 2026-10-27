import { Component, computed, input } from '@angular/core';
import { ExtrasResponse, OpeningDuel } from '../../services/report-api';

interface DuelRow {
  label: string;
  good: number;
  bad: number;
  goodLabel: string;
  badLabel: string;
  goodPct: number;
  sub: string;
}

const pct = (good: number, bad: number) => (good + bad === 0 ? 0 : (100 * good) / (good + bad));

@Component({
  imports: [],
  selector: 'app-duels-card',
  styleUrl: './duels-card.scss',
  templateUrl: './duels-card.html',
})
export class DuelsCard {
  readonly duels = input.required<OpeningDuel[]>();
  readonly extras = input.required<ExtrasResponse>();

  protected readonly rows = computed<DuelRow[]>(() => {
    const duels = this.duels();
    const { trades, clutches } = this.extras();

    const openingWon = duels.filter((d) => d.won).length;
    const openingLost = duels.length - openingWon;

    const clutchWon = clutches.filter((c) => c.won).length;
    const clutchLost = clutches.length - clutchWon;

    // Clutchs regroupés par nombre d'adversaires : "1v1 (1/2) · 1v2 (0/1)"
    const byVs = new Map<number, { won: number; total: number }>();
    for (const c of clutches) {
      const entry = byVs.get(c.vs) ?? { won: 0, total: 0 };
      entry.total++;
      if (c.won) entry.won++;
      byVs.set(c.vs, entry);
    }
    const clutchDetail = [...byVs.entries()]
      .sort((a, b) => a[0] - b[0])
      .map(([vs, { won, total }]) => `1v${vs} (${won}/${total})`)
      .join(' · ');

    return [
      {
        label: 'Opening duels',
        good: openingWon,
        bad: openingLost,
        goodLabel: 'Won',
        badLabel: 'Lost',
        goodPct: pct(openingWon, openingLost),
        sub: '',
      },
      {
        label: 'Teammate trades',
        good: trades.traded_deaths,
        bad: trades.untraded_deaths,
        goodLabel: 'Traded',
        badLabel: 'Untraded',
        goodPct: pct(trades.traded_deaths, trades.untraded_deaths),
        sub: `Trade kills: ${trades.trade_kills}`,
      },
      {
        label: 'Clutches',
        good: clutchWon,
        bad: clutchLost,
        goodLabel: 'Won',
        badLabel: 'Lost',
        goodPct: pct(clutchWon, clutchLost),
        sub: clutchDetail,
      },
    ];
  });
}