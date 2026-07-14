import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Landing } from './pages/Landing/Landing';
import { Login } from './pages/Auth/Login';
import { Register } from './pages/Auth/Register';
import { ForgotPassword } from './pages/Auth/ForgotPassword';
import { StudentDashboard } from './pages/Dashboards/StudentDashboard/StudentDashboard';
import { AdminDashboard } from './pages/Dashboards/AdminDashboard/AdminDashboard';
import { UniversityAdminDashboard } from './pages/Dashboards/UniversityAdminDashboard/UniversityAdminDashboard';
import { FacultyAdvisorDashboard } from './pages/Dashboards/FacultyAdvisorDashboard/FacultyAdvisorDashboard';

import { SessionProvider } from './context/SessionContext';
import { ProtectedRoute } from './assets/components/auth/ProtectedRoute/ProtectedRoute';
import { PublicOnlyRoute } from './assets/components/auth/PublicOnlyRoute/PublicOnlyRoute';

function App() {
  return (
    <BrowserRouter>
      <SessionProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<PublicOnlyRoute><Login /></PublicOnlyRoute>} />
          <Route path="/register" element={<PublicOnlyRoute><Register /></PublicOnlyRoute>} />
          <Route path="/forgot-password" element={<PublicOnlyRoute><ForgotPassword /></PublicOnlyRoute>} />
          
          {/* Dashboard Routes */}
          <Route path="/student-dashboard" element={<ProtectedRoute allowedRoles={['student']}><StudentDashboard /></ProtectedRoute>} />
          <Route path="/admin-dashboard" element={<ProtectedRoute allowedRoles={['system_admin']}><AdminDashboard /></ProtectedRoute>} />
          <Route path="/university-admin-dashboard" element={<ProtectedRoute allowedRoles={['student_affairs_office', 'dean_student_welfare']}><UniversityAdminDashboard /></ProtectedRoute>} />
          <Route path="/faculty-advisor-dashboard" element={<ProtectedRoute allowedRoles={['faculty_advisor']}><FacultyAdvisorDashboard /></ProtectedRoute>} />
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </SessionProvider>
    </BrowserRouter>
  );
}

export default App;
