import { inject, computed } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Auth } from '../services/auth';

export const membersOnlyGuard: CanActivateFn = () => {
  const router = inject(Router);
  const auth = inject(Auth);

  return auth.isSignedIn() ? true : router.createUrlTree(['/login']);
};

export const guestOnlyGuard: CanActivateFn = () => {
  const router = inject(Router);
  const auth = inject(Auth);

  return !auth.isSignedIn() ? true : router.createUrlTree(['/matches']);
};
