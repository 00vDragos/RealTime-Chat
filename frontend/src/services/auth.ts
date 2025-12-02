import { fetchJson } from '@/lib/api';
import type { AuthResult } from '@/features/auth/types';

export async function loginWithGoogleIdToken(idToken: string): Promise<AuthResult> {
  return fetchJson<AuthResult>('/auth/google', {
    method: 'POST',
    body: JSON.stringify({ id_token: idToken }),
  });
}
