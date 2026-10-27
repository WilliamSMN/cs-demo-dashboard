import { Component, computed, input, signal } from '@angular/core';
import { RoundImpact } from '../../services/report-api';

type Metric = 'damage' | 'kills';

@Component({
  imports: [],
  selector: 'app-round-impact-chart',
  styleUrl: './round-impact-chart.scss',
  templateUrl: './round-impact-chart.html',
})
export class RoundImpactChart {
  readonly rounds = input.required<RoundImpact[]>();
  protected readonly metric = signal<Metric>('damage');

  protected readonly bars = computed(() => {
    const metric = this.metric();
    const value = (r: RoundImpact) => (metric === 'damage' ? r.damage : r.kills);
    const max = Math.max(...this.rounds().map(value), 1);

    return this.rounds().map(r => ({
        round: r.round_num,
        height: Math.max((100*value(r)) / max,2),
        won: r.won,
        died: r.died,
        dots: Array.from({ length: r.kills }, (_, i) => i),
        label: `Round ${r.round_num}: ${r.damage} damage, ${r.kills} kills`
    }));
  });
}
