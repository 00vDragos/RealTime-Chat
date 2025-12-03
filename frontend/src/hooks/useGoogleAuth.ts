import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { loginWithGoogleIdToken } from '@/services/auth';

type Options = {
  onSuccess?: () => void;
  onError?: (message: string) => void;
};

export function useGoogleAuthHandlers(options: Options = {}) {
  const navigate = useNavigate();

  async function handleIdToken(credential?: string) {
    if (!credential) {
      const msg = 'No ID token received';
      options.onError?.(msg);
      toast.error(msg);
      return;
    }
    try {
      await loginWithGoogleIdToken(credential);
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

  return { handleIdToken, handleError };
}
