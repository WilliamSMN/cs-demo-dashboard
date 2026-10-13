import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_URL } from '../config';

export interface HealthResponse {
  status: string;
}

export interface MatchMeta {
  id: string;
  filename: string | null;
  status: 'processing' | 'ready' | 'failed';
  map_name: string | null;
  tickrate: number | null;
  rounds: number | null;
  error: string | null;
}

export interface PlayerStats {
  steamid: string;
  name: string;
  team: number | null;
  kills: number;
  deaths: number;
  assists: number;
  adr: number;
  hs_pct: number;
}

export interface StatsResponse {
  players: PlayerStats[];
  unattributed_deaths: number;
}

@Injectable({ providedIn: 'root' })
export class MatchesApi {
  private readonly http = inject(HttpClient);

  health(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${API_URL}/health`);
  }

  list(): Observable<MatchMeta[]> {
    return this.http.get<MatchMeta[]>(`${API_URL}/matches`);
  }

  upload(file: File): Observable<MatchMeta> {
    const body = new FormData();
    body.append('file', file);
    return this.http.post<MatchMeta>(`${API_URL}/matches`, body);
  }

  getStats(matchId: string): Observable<StatsResponse> {
    return this.http.get<StatsResponse>(`${API_URL}/matches/${matchId}/stats`);
  }
}
