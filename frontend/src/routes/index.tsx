import type { RouteObject } from 'react-router-dom';
import AuthPage from '../features/auth/AuthPage';
import ChatPage from '@/features/chat/ChatPage';
// import { ThemeSwitcher } from '@/theme/ThemeSwitcher';
import { Navigate } from 'react-router-dom';

const Home = () => <Navigate to="/auth" replace />;

const routes: RouteObject[] = [
    {
        path: '/',
        element: <Home />,
    },
    {
        path: '/auth',
        element: <AuthPage />,
    },
    {
        path: '/chat',
        element: <ChatPage />,
    },
];

export default routes;
