export function sumBy<T>(items: readonly T[], key: keyof T): number {
  return items.reduce((sum, item) => sum + ((item[key] as number | undefined) ?? 0), 0);
}

export function ratio(part: number, total: number): number {
  return total > 0 ? part / total : 0;
}
