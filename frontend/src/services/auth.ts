import { fetchJson } from '@/lib/api';
import type { AuthResult } from '@/features/auth/types';

type MessageResponse = {
  message: string;
};

export async function exchangeGoogleAuthCode(code: string): Promise<AuthResult> {
  return fetchJson<AuthResult>('/auth/google/callback', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}

export async function loginWithEmailPassword(email: string, password: string): Promise<AuthResult> {
  return fetchJson<AuthResult>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function registerUser(email: string, password: string, displayName?: string | null): Promise<AuthResult> {
  return fetchJson<AuthResult>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      email,
      password,
      display_name: displayName ?? null,
    }),
  });
}

export async function logoutUser(refreshToken: string): Promise<MessageResponse> {
  return fetchJson<MessageResponse>('/auth/logout', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}
