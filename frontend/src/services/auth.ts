import { fetchJson } from '@/lib/api';
import type { AuthResult } from '@/features/auth/types';

export async function loginWithGoogle(accessToken: string): Promise<AuthResult> {
  return fetchJson<AuthResult>('/auth/google', {
    method: 'POST',
    body: JSON.stringify({ access_token: accessToken }),
  });
}
