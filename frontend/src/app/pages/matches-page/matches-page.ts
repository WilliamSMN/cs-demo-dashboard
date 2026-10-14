import { Component, inject } from '@angular/core';
import { UploadForm } from '../../components/upload-form/upload-form';
import { MatchList } from '../../components/match-list/match-list';
import { Auth } from '../../services/auth';
import { AuthBar } from '../../components/auth-bar/auth-bar';

@Component({
  imports: [UploadForm, MatchList, AuthBar],
  selector: 'app-matches-page',
  styleUrl: './matches-page.scss',
  templateUrl: './matches-page.html',
})
export class MatchesPage {
  protected readonly auth = inject(Auth);
}
