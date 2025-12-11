import { useCallback, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { clearAuthSession, getStoredSession } from '@/features/auth/storage';
import { logoutUser } from '@/services/auth';

export function useLogout() {
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const logout = useCallback(async () => {
    if (isLoggingOut) {
      return;
    }

    setIsLoggingOut(true);
    let serverSuccess = false;

    try {
      const session = getStoredSession();
      const refreshToken = session?.refreshToken;

      if (refreshToken) {
        await logoutUser(refreshToken);
      }

      serverSuccess = true;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Logout failed';
      toast.error(message);
    } finally {
      clearAuthSession();
      setIsLoggingOut(false);

      if (serverSuccess) {
        toast.success('Logged out');
      }

      navigate('/auth', { replace: true });
    }
  }, [isLoggingOut, navigate]);

  return { logout, isLoggingOut } as const;
}
