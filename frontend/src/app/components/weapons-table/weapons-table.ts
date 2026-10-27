import { Component, computed, input } from '@angular/core';
import { WeaponStats } from '../../services/report-api';

// Dictionnaire : à gauche le nom brut de la démo, à droite le nom affiché
const NAMES: Record<string, string> = {
  ak47: 'AK-47',
  m4a1_silencer: 'M4A1-S',
  m4a1: 'M4A4',
  usp_silencer: 'USP-S',
  hkp2000: 'P2000',
  awp: 'AWP',
  deagle: 'Desert Eagle',
  glock: 'Glock-18',
  mp9: 'MP9',
  hegrenade: 'HE grenade',
  inferno: 'Molotov',
};

interface Row {
  name: string;
  kills: number;
  hs: string;
  damage: number;
}

@Component({
  imports: [],
  selector: 'app-weapons-table',
  styleUrl: './weapons-table.scss',
  templateUrl: './weapons-table.html',
})
export class WeaponsTable {
  readonly weapons = input.required<WeaponStats[]>();

  protected readonly rows = computed<Row[]>(() =>
    this.weapons().map((w) => ({
      name: NAMES[w.weapon] ?? w.weapon,
      kills: w.kills,
      hs: w.kills === 0 ? '-' : `${Math.round((100 * w.headshots) / w.kills)}%`,
      damage: w.damage,
    })),
  );
}