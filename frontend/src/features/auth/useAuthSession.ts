import { useSyncExternalStore } from 'react';
import { getStoredSession, subscribeToAuthSession } from './storage';
import type { SessionUser } from './types';

export function useAuthSession() {
  return useSyncExternalStore(subscribeToAuthSession, getStoredSession, () => null);
}

export function useAuthUser(): SessionUser | null {
  return useAuthSession()?.user ?? null;
}

export function useAuthUserId(): string | null {
  return useAuthUser()?.id ?? null;
}
