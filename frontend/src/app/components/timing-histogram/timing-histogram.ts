import { Component, computed, input } from '@angular/core';
import { KillEvent } from '../../services/report-api';

interface Bin {
  label: string;
  kills: number;
  deaths: number;
  killsPct: number;
  deathsPct: number;
}

@Component({
  imports: [],
  selector: 'app-timing-histogram',
  styleUrl: './timing-histogram.scss',
  templateUrl: './timing-histogram.html',
})
export class TimingHistogram {
  readonly events = input.required<KillEvent[]>();

  protected readonly bins = computed<Bin[]>(() => {
    const counts = Array.from({ length: 7 }, (_, i) => ({
      label: i < 6 ? `${i * 15}-${(i + 1) * 15}s` : '90+s',
      kills: 0,
      deaths: 0,
    }));

    for (const e of this.events()) {
      const index = Math.min(Math.floor(e.seconds / 15), 6);
      if (e.kind === 'kill') counts[index].kills++;
      else counts[index].deaths++;
    }

    const max = Math.max(...counts.flatMap((b) => [b.kills, b.deaths]), 1);

    return counts.map((b) => ({
      ...b,
      killsPct: (100 * b.kills) / max,
      deathsPct: (100 * b.deaths) / max,
    }));
  });

  protected readonly totals = computed(() => {
    const pts = this.events();
    return {
      kills: pts.filter((p) => p.kind === 'kill').length,
      deaths: pts.filter((p) => p.kind === 'death').length,
    };
  });
}
