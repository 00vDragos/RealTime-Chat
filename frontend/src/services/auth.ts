import { fetchJson } from '@/lib/api';
import type { AuthResult } from '@/features/auth/types';

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
