import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LearningPath from './pages/LearningPath';
import CarbonTracker from './pages/CarbonTracker';
import TreePlantations from './pages/TreePlantations';

function App() {
  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/learning/:id" element={<LearningPath />} />
          <Route path="/carbon" element={<CarbonTracker />} />
          <Route path="/trees" element={<TreePlantations />} />
        </Routes>
      </Router>
      <Toaster />
    </>
  );
}

export default App;