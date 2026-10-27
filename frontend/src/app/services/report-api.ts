import { PlayerStats } from './matches-api';

export type Side = 'ct' | 't';

export type Kind = 'kill' | 'death';

export interface PlayerReportSummary extends PlayerStats {
    rounds: number;
    kast: number | null;
    rating: number | null;
}

export interface RoundImpact {
    round_num: number;
    side: Side;
    won: boolean;
    kills: number;
    headshots: number;
    damage: number;
    died: boolean;
}

export interface RoundImpactResponse {
    rounds: RoundImpact[];
}

export interface KillEvent{
    round_num: number;
    side: Side;
    kind: Kind;
    seconds: number;
}

export interface KillTimingResponse{
    events: KillEvent[];
}

export interface OpeningDuel{
    round_num: number;
    side: Side;
    won: boolean;
}

export interface OpeningDuelsResponse{
    duels: OpeningDuel[];
}

export interface ClutchRound{
    round_num: number;
    vs: number;
    won: boolean;
}

export interface TradeCounts{
    trade_kills: number;
    traded_deaths: number;
    untraded_deaths: number;
}

export interface UtilityCounts{
    flashes_thrown: number;
    enemies_flashed: number;
    team_flashed: number;
    flash_assists: number;
    he_damage: number;
    molotov_damage: number;
    blind_time: number;
}

export interface ExtrasResponse{
    trades: TradeCounts;
    utility: UtilityCounts;
    clutches: ClutchRound[];
}

export interface WeaponStats{
    weapon: string;
    kills: number;
    headshots: number;
    damage: number;
}

export interface OpponentRecord{
    steamid: string;
    name: string;
    killed: number;
    killed_by: number;
}

export interface WeaponsResponse{
    weapons: WeaponStats[];
    opponents: OpponentRecord[];
}

export interface PositionEvent{
    round_num: number;
    side: Side;
    kind: Kind;
    x: number;
    y: number;
    z: number;
    px: number | null;
    py: number | null;
}

export interface PositionsResponse{
    map_name: string | null;
    radar_size: number;
    events: PositionEvent[];
}

export type ProfileKey = 'aim' | 'impact' | 'utility' | 'clutch' | 'opening' | 'trade';

export interface ProfileAxis{
    key: ProfileKey;
    score: number | null;
    values: Record<string, number | null>;
}

export interface ProfileResponse{
    reference: number;
    axes: ProfileAxis[]
}
