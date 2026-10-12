import { Component, inject  } from '@angular/core';
import { MatchesStore } from '../../services/matches-store';

@Component({
  selector: 'app-match-list',
  styleUrl: './match-list.scss',
  templateUrl: './match-list.html',
})
export class MatchList {
  protected readonly store = inject(MatchesStore);
}
