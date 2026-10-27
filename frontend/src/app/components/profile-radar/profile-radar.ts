import { Component, computed, input } from '@angular/core';
import { ProfileKey, ProfileResponse } from '../../services/report-api';

const CX = 180;
const CY = 150;
const RADIUS = 100;

function point(i: number, n: number, ratio: number) {
  const angle = -Math.PI / 2 + (i * 2 * Math.PI) / n;
  return { x: CX + RADIUS * ratio * Math.cos(angle), y: CY + RADIUS * ratio * Math.sin(angle) };
}

const LABELS: Record<ProfileKey, string> = {
  aim: 'Aim',
  impact: 'Impact',
  utility: 'Utility',
  clutch: 'Clutch',
  opening: 'Opening',
  trade: 'Trade',
};

const toPoints = (pts: { x: number; y: number }[]) =>
  pts.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');

@Component({
  imports: [],
  selector: 'app-profile-radar',
  styleUrl: './profile-radar.scss',
  templateUrl: './profile-radar.html',
})
export class ProfileRadar {
  readonly profile = input.required<ProfileResponse>();

  private readonly axesData = computed(() => {
    const axes = this.profile().axes;
    return { axes, n: axes.length };
  });

  protected readonly valuePoints = computed(() => {
    const { axes, n } = this.axesData();
    return toPoints(axes.map((a, i) => point(i, n, (a.score ?? 0) / 100)));
  });

  protected readonly referencePoints = computed(() => {
    const { axes, n } = this.axesData();
    const ratio = this.profile().reference / 100;
    return toPoints(axes.map((_, i) => point(i, n, ratio)));
  });

  protected readonly rings = computed(() => {
    const { axes, n } = this.axesData();
    return [1 / 3, 2 / 3, 1].map((ratio) =>
       toPoints(axes.map((_, i) => point(i, n, ratio))),
     );
  });

  protected readonly axes = computed(() => {
    const { axes, n } = this.axesData();
    return axes.map((a, i) => ({
        label: LABELS[a.key],
        score: a.score === null? '-' : Math.round(a.score),
        spoke: point(i,n,1),
        labelPos: point(i,n,1.22)
    }));
  });

  protected readonly description = computed(() =>
    this.axes().map((a) => `${a.label} ${a.score}`).join(', '),
  );
}
