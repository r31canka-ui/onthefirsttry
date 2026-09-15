import { CurrentUser } from './types';

/**
 * Where to land a user right after login (or at `/`). Every role can read
 * appointments.read.own at minimum, so /calendar is the safe universal
 * fallback - hardcoding '/dashboard' sent Front Desk (no reports.read)
 * straight into a 403 on their very first screen after logging in.
 */
export function getDefaultRoute(user: CurrentUser): string {
  if (user.permissions.includes('reports.read')) return '/dashboard';
  if (user.permissions.includes('contacts.read')) return '/contacts';
  return '/calendar';
}
