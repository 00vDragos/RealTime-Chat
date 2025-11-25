import './App.css';
import { Button } from "@/components/ui/button";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AuthPage from './features/auth/AuthPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/" element={
          <Button>
            Click me
          </Button>
        } />
      </Routes>
    </Router>
  );
}

export default App;
