import { Component, computed, input, signal } from '@angular/core';
import { PositionsResponse, Side } from '../../services/report-api';
import { API_URL } from '../../config';

type SideFilter = 'all' | Side;

@Component({
  imports: [],
  selector: 'app-kill-map',
  styleUrl: './kill-map.scss',
  templateUrl: './kill-map.html',
})
export class KillMap {
  readonly radarOverride = input<string | null>(null);
  readonly positions = input.required<PositionsResponse>();
  protected readonly imageFailed = signal(false);
  protected readonly side = signal<SideFilter>('all');

  protected readonly radarUrl = computed(() => {
    const name = this.positions().map_name;
    return this.radarOverride() ? this.radarOverride() :  name ? `${API_URL}/maps/${name}/radar` : null;
  });

  protected readonly sides: { key: SideFilter; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'ct', label: 'CT' },
    { key: 't', label: 'T' },
  ];


  protected readonly points = computed(() => {
    const side = this.side();
    return this.positions().events.flatMap((e) =>
      (side !== 'all' && e.side !== side) || e.px === null || e.py === null
        ? []
        : [{ x: e.px, y: e.py, kind: e.kind, label: `Round ${e.round_num} (${e.side}): ${e.kind}` }],
    );
  });

  protected readonly counts = computed(() => {
    const pts = this.points();
    return {
      kills: pts.filter((p) => p.kind === 'kill').length,
      deaths: pts.filter((p) => p.kind === 'death').length,
    };
  });
}
