import './App.css';
import { BrowserRouter, useRoutes } from 'react-router-dom';
import routes from './routes';
import { ThemeProvider } from './theme/ThemeProvider';
import { Toaster } from '@/components/ui/sonner';

function AppRoutes() {
  return useRoutes(routes);
}


function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AppRoutes />
        <Toaster position="bottom-right" />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;