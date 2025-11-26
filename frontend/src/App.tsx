import './App.css';
import { BrowserRouter, useRoutes } from 'react-router-dom';
import routes from './routes';
import { ThemeProvider } from './theme/ThemeProvider';

function AppRoutes() {
  return useRoutes(routes);
}


function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;