import type { ReactNode } from 'react';
import type { RouteObject } from 'react-router-dom';
import AuthPage from '../features/auth/AuthPage';
import ChatPage from '@/features/chat/ChatPage';
import { Navigate } from 'react-router-dom';
import { useAuthUserId } from '@/features/auth/useAuthSession';

const Home = () => {
    const userId = useAuthUserId();
    return <Navigate to={userId ? '/chat' : '/auth'} replace />;
};

const ProtectedRoute = ({ children }: { children: ReactNode }) => {
    const userId = useAuthUserId();
    if (!userId) {
        return <Navigate to="/auth" replace />;
    }
    return <>{children}</>;
};

const GuestOnlyRoute = ({ children }: { children: ReactNode }) => {
    const userId = useAuthUserId();
    if (userId) {
        return <Navigate to="/chat" replace />;
    }
    return <>{children}</>;
};

const routes: RouteObject[] = [
    {
        path: '/',
        element: <Home />,
    },
    {
        path: '/auth',
        element: (
            <GuestOnlyRoute>
                <AuthPage />
            </GuestOnlyRoute>
        ),
    },
    {
        path: '/chat',
        element: (
            <ProtectedRoute>
                <ChatPage />
            </ProtectedRoute>
        ),
    },
];

export default routes;
