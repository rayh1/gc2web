export interface Crumb {
  label: string;
  href?: string;
}

export const initialMobileMenuExpanded = false;

export function nextMobileMenuExpanded(expanded: boolean): boolean {
  return !expanded;
}

export function normalizeBreadcrumbs(items: Crumb[] = []): Crumb[] {
  return items.filter((item) => item.label.trim().length > 0);
}
