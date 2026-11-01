import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import Jobs from './pages/Jobs';
import Skills from './pages/Skills';

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', minHeight: '100vh' }}>
        <Sidebar />
        <main style={{ flex: 1, overflowY: 'auto' }}>
          <Routes>
            <Route path="/"      element={<Overview />} />
            <Route path="/jobs"  element={<Jobs />} />
            <Route path="/skills" element={<Skills />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}