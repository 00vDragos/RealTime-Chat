import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { exchangeGoogleAuthCode } from '@/services/auth';
import { persistAuthSession } from '@/features/auth/storage';

type Options = {
  onSuccess?: () => void;
  onError?: (message: string) => void;
};

export function useGoogleAuthHandlers(options: Options = {}) {
  const navigate = useNavigate();

  async function handleAuthCode(code?: string) {
    if (!code) {
      const msg = 'No authorization code received';
      options.onError?.(msg);
      toast.error(msg);
      return;
    }
    try {
      const authResult = await exchangeGoogleAuthCode(code);
      persistAuthSession(authResult);
    } catch (e: any) {
      const msg = e?.message || 'Login failed';
      options.onError?.(msg);
      toast.error(msg);
      return;
    }
    toast.success('Logged in with Google');
    options.onSuccess?.();
    navigate('/chat');
  }

  function handleError() {
    const msg = 'Google authentication failed';
    options.onError?.(msg);
    toast.error(msg);
  }

  return { handleAuthCode, handleError };
}
