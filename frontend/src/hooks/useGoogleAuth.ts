import { useNavigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import { toast } from 'sonner';
import { loginWithGoogle } from '@/services/auth';

type Options = {
  onSuccess?: () => void;
  onError?: (message: string) => void;
};

export function useGoogleAuth(options: Options = {}) {
  const navigate = useNavigate();

  const startGoogleLogin = useGoogleLogin({
    flow: 'implicit',
    onSuccess: async (tokenResponse) => {
      const accessToken = tokenResponse.access_token;
      if (!accessToken) {
        const msg = 'No access token received';
        options.onError?.(msg);
        toast.error(msg);
        return;
      }
      try {
        await loginWithGoogle(accessToken);
      } catch (e: any) {
        const msg = e?.message || 'Login failed';
        options.onError?.(msg);
        toast.error(msg);
        return;
      }
      toast.success('Logged in with Google');
      options.onSuccess?.();
      navigate('/chat');
    },
    onError: () => {
      const msg = 'Google authentication failed';
      options.onError?.(msg);
      toast.error(msg);
    },
  });

  return { startGoogleLogin };
}
