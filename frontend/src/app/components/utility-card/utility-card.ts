import { Component, computed, input } from '@angular/core';
import { UtilityCounts } from '../../services/report-api';
import { computeMsgId } from '@angular/compiler';

interface Stat {
  label: string;
  value: string;
  sub: string;
  tone: 'neutral' | 'warn';
}

@Component({
  imports: [],
  selector: 'app-utility-card',
  styleUrl: './utility-card.scss',
  templateUrl: './utility-card.html',
})
export class UtilityCard {
  readonly utility = input.required<UtilityCounts>();

  protected readonly stats = computed<Stat[]>(() => {
    const u = this.utility();
    const avg = u.enemies_flashed === 0 ? null : u.blind_time / u.enemies_flashed;
    return [ 
      {
        label: 'Utility damage',
        value: `${u.he_damage + u.molotov_damage}`,
        sub: `HE ${u.he_damage} / Molotov ${u.molotov_damage}`,
        tone: 'neutral',
      },
      {
        label: 'Flashes thrown',
        value: `${u.flashes_thrown}`,
        sub: '',
        tone: 'neutral',
      },
      {
        label: 'Enemies flashed',
        value: `${u.enemies_flashed}`,
        sub: u.flashes_thrown > 0 ? `${ u.enemies_flashed / u.flashes_thrown} per flash` : '',
        tone: 'neutral',
      },
      {
        label: 'Avg blind time',
        value: avg === null ? '-' : `${avg.toFixed(1)} s`,
        sub: `Total ${u.blind_time.toFixed(1)} s`,
        tone: 'neutral',
      },
      {
        label: 'Teammates flashed',
        value: `${u.team_flashed}`,
        sub: '',
        tone: u.team_flashed > 0 ? 'warn' : 'neutral',
      },
      {
        label: 'Flash assists',
        value: `${u.flash_assists}`,
        sub: '',
        tone: 'neutral',
      },
    ];
  });
}
