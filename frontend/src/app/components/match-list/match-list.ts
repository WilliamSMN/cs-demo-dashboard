import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatchesStore } from '../../services/matches-store';

@Component({
  imports: [RouterLink],
  selector: 'app-match-list',
  styleUrl: './match-list.scss',
  templateUrl: './match-list.html',
})
export class MatchList {
  protected readonly store = inject(MatchesStore);
}
