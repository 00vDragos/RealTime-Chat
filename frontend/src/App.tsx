import './App.css';
import { BrowserRouter, useRoutes } from 'react-router-dom';
import routes from './routes';
import { ThemeProvider } from './theme/ThemeProvider';
import { Toaster } from '@/components/ui/sonner';
import { GoogleOAuthProvider } from '@react-oauth/google';

function AppRoutes() {
  return useRoutes(routes);
}


function App() {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID!;
  return (
    <ThemeProvider>
      <GoogleOAuthProvider clientId={clientId}>
        <BrowserRouter>
          <AppRoutes />
          <Toaster position="bottom-right" />
        </BrowserRouter>
      </GoogleOAuthProvider>
    </ThemeProvider>
  );
}

export default App;