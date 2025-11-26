import type { RouteObject } from 'react-router-dom';
import AuthPage from '../features/auth/AuthPage';
import ChatPage from '@/features/chat/ChatPage';
import { ThemeSwitcher } from '@/theme/ThemeSwitcher';

    // Example Home component inline for now
const Home = () => <ThemeSwitcher />;

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
