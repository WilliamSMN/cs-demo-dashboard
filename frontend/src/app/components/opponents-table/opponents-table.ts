import { Component, computed, input } from '@angular/core';
import { OpponentRecord } from '../../services/report-api';

interface Row {
  name: string;
  killed: number;
  killedBy: number;
  tone: 'good' | 'bad' | 'even';
}

@Component({
  imports: [],
  selector: 'app-opponents-table',
  styleUrl: './opponents-table.scss',
  templateUrl: './opponents-table.html',
})
export class OpponentsTable {
  readonly opponents = input.required<OpponentRecord[]>();

  protected readonly rows = computed<Row[]>(() =>
    this.opponents().map((o) => ({
      name: o.name,
      killed: o.killed,
      killedBy: o.killed_by,
      tone: o.killed > o.killed_by ? 'good' : o.killed < o.killed_by ? 'bad' : 'even',
    })),
  );

  protected readonly totals = computed(() => ({
    killed: this.rows().reduce((sum, x) => sum + x.killed, 0),
    killedBy: this.rows().reduce((sum, x) => sum + x.killedBy, 0),
  }));
}