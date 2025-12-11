import type { AuthResult, AuthSession, SessionUser } from './types';

const STORAGE_KEY = 'rtc.auth.session';

type SessionSubscriber = () => void;

const subscribers = new Set<SessionSubscriber>();
let inMemorySession: AuthSession | null = null;
let hasLoadedInitialSession = false;

function notifySubscribers() {
  subscribers.forEach((listener) => {
    try {
      listener();
    } catch (error) {
      console.error('[auth] subscriber failed', error);
    }
  });
}

function setInMemorySession(session: AuthSession | null) {
  inMemorySession = session;
  hasLoadedInitialSession = true;
  notifySubscribers();
}

function mapUser(apiUser: AuthResult['user']): SessionUser {
  return {
    id: apiUser.id,
    email: apiUser.email,
    displayName: apiUser.display_name ?? undefined,
    avatarUrl: apiUser.avatar_url ?? undefined,
    provider: apiUser.provider ?? undefined,
    providerSub: apiUser.provider_id ?? undefined,
    createdAt: apiUser.created_at ?? undefined,
    updatedAt: apiUser.updated_at ?? undefined,
  };
}

function writeSessionToStorage(session: AuthSession | null) {
  if (typeof window === 'undefined') {
    return;
  }
  if (session) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
}

export function persistAuthSession(result: AuthResult): AuthSession {
  const session: AuthSession = {
    accessToken: result.access_token,
    refreshToken: result.refresh_token,
    tokenType: result.token_type,
    user: mapUser(result.user),
  };

  writeSessionToStorage(session);
  setInMemorySession(session);

  return session;
}

export function getStoredSession(): AuthSession | null {
  if (hasLoadedInitialSession) {
    return inMemorySession;
  }
  if (typeof window === 'undefined') {
    return null;
  }
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    inMemorySession = null;
    hasLoadedInitialSession = true;
    return null;
  }
  try {
    inMemorySession = JSON.parse(raw) as AuthSession;
    hasLoadedInitialSession = true;
    return inMemorySession;
  } catch {
    inMemorySession = null;
    hasLoadedInitialSession = true;
    return null;
  }
}

export function clearAuthSession() {
  writeSessionToStorage(null);
  setInMemorySession(null);
}

export function getStoredAccessToken(): string | undefined {
  return getStoredSession()?.accessToken;
}

export function updateSessionAvatarUrl(avatarUrl: string) {
  const session = getStoredSession();
  if (!session || !session.user) return;
  const next: AuthSession = {
    ...session,
    user: {
      ...session.user,
      avatarUrl: avatarUrl || undefined,
    },
  };
  writeSessionToStorage(next);
  setInMemorySession(next);
}

export type ApiUserResponse = {
  id: string;
  email: string;
  display_name?: string | null;
  avatar_url?: string | null;
  provider?: string | null;
  provider_id?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export function updateSessionUserFromApi(user: ApiUserResponse) {
  const session = getStoredSession();
  if (!session) return;
  const next: AuthSession = {
    ...session,
    user: {
      id: user.id,
      email: user.email,
      displayName: user.display_name ?? undefined,
      avatarUrl: user.avatar_url ?? undefined,
      provider: user.provider ?? undefined,
      providerSub: user.provider_id ?? undefined,
      createdAt: user.created_at ?? undefined,
      updatedAt: user.updated_at ?? undefined,
    },
  };
  writeSessionToStorage(next);
  setInMemorySession(next);
}

export function subscribeToAuthSession(listener: SessionSubscriber) {
  subscribers.add(listener);
  return () => {
    subscribers.delete(listener);
  };
}

if (typeof window !== 'undefined') {
  window.addEventListener('storage', (event) => {
    if (event.key !== STORAGE_KEY) {
      return;
    }
    if (event.newValue) {
      try {
        inMemorySession = JSON.parse(event.newValue) as AuthSession;
      } catch {
        inMemorySession = null;
      }
    } else {
      inMemorySession = null;
    }
    hasLoadedInitialSession = true;
    notifySubscribers();
  });
}
