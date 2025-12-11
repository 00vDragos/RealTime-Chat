import { getStoredSession } from '@/features/auth/storage';

export function getAuthenticatedUserId(): string | null {
	return getStoredSession()?.user.id ?? null;
}
