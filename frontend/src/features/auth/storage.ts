import type { AuthResult, AuthSession, SessionUser } from './types';

const STORAGE_KEY = 'rtc.auth.session';

function mapUser(apiUser: AuthResult['user']): SessionUser {
  return {
    id: apiUser.id,
    email: apiUser.email,
    displayName: apiUser.display_name ?? undefined,
    avatarUrl: apiUser.avatar_url ?? undefined,
    provider: apiUser.provider ?? undefined,
    providerSub: apiUser.provider_sub ?? undefined,
    createdAt: apiUser.created_at ?? undefined,
    updatedAt: apiUser.updated_at ?? undefined,
  };
}

export function persistAuthSession(result: AuthResult): AuthSession {
  const session: AuthSession = {
    accessToken: result.access_token,
    refreshToken: result.refresh_token,
    tokenType: result.token_type,
    user: mapUser(result.user),
  };

  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }

  return session;
}

export function getStoredSession(): AuthSession | null {
  if (typeof window === 'undefined') {
    return null;
  }
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    return null;
  }
}

export function clearAuthSession() {
  if (typeof window === 'undefined') {
    return;
  }
  localStorage.removeItem(STORAGE_KEY);
}

export function getStoredAccessToken(): string | undefined {
  return getStoredSession()?.accessToken;
}
