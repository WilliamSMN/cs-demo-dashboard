import { Routes } from '@angular/router';
import { MatchesPage } from './pages/matches-page/matches-page';
import { MatchDetail } from './pages/match-detail/match-detail';

export const routes: Routes = [
  { path: 'matches', component: MatchesPage },
  { path: 'matches/:id', component: MatchDetail },
  { path: '', redirectTo: 'matches', pathMatch: 'full' },
  { path: '**', redirectTo: 'matches' },
];
