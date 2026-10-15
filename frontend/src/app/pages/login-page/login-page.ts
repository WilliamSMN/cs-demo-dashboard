import { Component, inject, input } from '@angular/core';
import { Auth } from '../../services/auth';

@Component({
  selector: 'app-login-page',
  styleUrl: './login-page.scss',
  templateUrl: './login-page.html',
})
export class LoginPage {
  protected readonly auth = inject(Auth);
  readonly error = input<string>();
}
