import { Component, inject } from '@angular/core';
import { UploadForm } from '../../components/upload-form/upload-form';
import { MatchList } from '../../components/match-list/match-list';
import { Auth } from '../../services/auth';

@Component({
  imports: [UploadForm, MatchList],
  selector: 'app-matches-page',
  styleUrl: './matches-page.scss',
  templateUrl: './matches-page.html',
})
export class MatchesPage {
  protected readonly auth = inject(Auth);
}