import { Routes } from '@angular/router';
import { MatchesPage } from './pages/matches-page/matches-page';
import { MatchDetail } from './pages/match-detail/match-detail';
import { LoginPage } from './pages/login-page/login-page';
import { guestOnlyGuard, membersOnlyGuard } from './guards/auth-guard';
import { HomePage } from './pages/home-page/home-page';
import { inject } from '@angular/core';
import { Auth } from './services/auth';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: () => (inject(Auth).isSignedIn() ? 'matches' : 'home'),
  },
  { path: 'home', component: HomePage },
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
  { path: '**', redirectTo: () => (inject(Auth).isSignedIn() ? 'matches' : 'home')},
];
