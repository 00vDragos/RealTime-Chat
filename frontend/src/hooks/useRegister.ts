import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { registerUser } from '@/services/auth';
import { persistAuthSession } from '@/features/auth/storage';

export function useRegister() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const register = async (email: string, password: string, displayName?: string) => {
    setIsSubmitting(true);
    try {
      const authResult = await registerUser(email, password, displayName);
      persistAuthSession(authResult);
      toast.success('Account created!');
      navigate('/chat');
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Registration failed';
      toast.error(message);
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  };

  return { register, isSubmitting } as const;
}
