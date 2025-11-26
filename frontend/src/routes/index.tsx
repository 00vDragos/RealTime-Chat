import type { RouteObject } from 'react-router-dom';
import AuthPage from '../features/auth/AuthPage';
import { Button } from '@/components/ui/button';
import ChatPage from '@/features/chat/ChatPage';

// Example Home component inline for now
const Home = () => <Button>Click me</Button>;

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
