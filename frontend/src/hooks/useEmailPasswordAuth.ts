import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { loginWithEmailPassword } from '@/services/auth';
import { persistAuthSession } from '@/features/auth/storage';

export function useEmailPasswordAuth() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const login = async (email: string, password: string) => {
    setIsSubmitting(true);
    try {
      const authResult = await loginWithEmailPassword(email, password);
      persistAuthSession(authResult);
      toast.success('Welcome back!');
      navigate('/chat');
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Login failed';
      toast.error(message);
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  };

  return { login, isSubmitting } as const;
}
