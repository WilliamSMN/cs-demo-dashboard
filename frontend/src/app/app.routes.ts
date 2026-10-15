import { Routes } from '@angular/router';
import { MatchesPage } from './pages/matches-page/matches-page';
import { MatchDetail } from './pages/match-detail/match-detail';
import { LoginPage } from './pages/login-page/login-page';
import { guestOnlyGuard, membersOnlyGuard } from './guards/auth-guard';

export const routes: Routes = [
  {
    path: '',
    canActivate: [guestOnlyGuard],
    children: [{ path: 'login', component: LoginPage }],
  },
  {
    path: '',
    canActivate: [membersOnlyGuard],
    children: [
      { path: 'matches', component: MatchesPage },
      { path: 'matches/:id', component: MatchDetail },
    ],
  },
  { path: '', redirectTo: 'matches', pathMatch: 'full' },
  { path: '**', redirectTo: 'matches' },
];
