import { Component, inject, signal } from '@angular/core';
import { describeHttpError } from '../../services/http-errors';

import { MatchesApi, MatchMeta } from '../../services/matches-api';
import { MatchesStore } from '../../services/matches-store';

type UploadState =
  | { kind: 'idle' }
  | { kind: 'uploading' }
  | { kind: 'error'; message: string }
  | { kind: 'uploaded'; match: MatchMeta };

@Component({
  selector: 'app-upload-form',
  styleUrl: './upload-form.scss',
  templateUrl: './upload-form.html',
})
export class UploadForm {
  private readonly api = inject(MatchesApi);
  readonly uploadState = signal<UploadState>({ kind: 'idle' });
  protected readonly store = inject(MatchesStore);

  onFileChosen(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0]; // File | undefined : l'utilisateur a pu annuler

    if (file) {
      this.uploadState.set({ kind: 'uploading' });
      this.api.upload(file).subscribe({
        next: (match) => {
          this.uploadState.set({ kind: 'uploaded', match });
          this.store.refresh();
        },
        error: (err: unknown) => {
          console.error(err);
          this.uploadState.set({ kind: 'error', message: describeHttpError(err) });
        },
      });
    } else {
      this.uploadState.set({ kind: 'error', message: 'No files provided.' });
    }
  }
}
