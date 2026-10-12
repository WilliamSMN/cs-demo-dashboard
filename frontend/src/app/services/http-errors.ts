import { HttpErrorResponse } from '@angular/common/http';

export function describeHttpError(err: unknown): string {
  if (!(err instanceof HttpErrorResponse)) {
    return 'Something went wrong. Please try again.';
  }

  // Aucune réponse reçue : backend éteint, réseau coupé ou CORS refusé
  if (err.status === 0) {
    return 'Cannot reach the server. Check that the backend is running.';
  }

  // Erreurs serveur : on n'expose pas de détail interne
  if (err.status >= 500) {
    return 'Server error. Please try again later.';
  }

  if (err.status === 400) {
    return 'The server rejected this file. Please choose a .dem file.';
  }

  if (err.status === 422) {
    return 'The server rejected the submitted data.';
  }

  return `Request failed (HTTP ${err.status}).`;
}

// Le corps de l'erreur est inconnu : on vérifie sa forme avant de l'utiliser
function extractDetail(body: unknown): string | null {
  if (typeof body === 'object' && body !== null && 'detail' in body) {
    const { detail } = body;
    return typeof detail === 'string' ? detail : null;
  }
  return null;
}
