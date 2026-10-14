import { Component, inject } from '@angular/core';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-auth-bar',
  styleUrl: './auth-bar.scss',
  templateUrl: './auth-bar.html',
})
export class AuthBar {
  protected readonly auth = inject(Auth);
}
