import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!user) return null;

  const roleLinks = {
    PATIENT: [
      { to: '/patient', label: 'Dashboard' },
    ],
    DOCTOR: [
      { to: '/doctor', label: 'Dashboard' },
    ],
    ADMIN: [
      { to: '/admin', label: 'Dashboard' },
    ],
    EMERGENCY: [
      { to: '/emergency', label: 'Quick Entry' },
    ],
    DEPARTMENT: [
      { to: '/department', label: 'Orders' },
    ],
  };

  const links = roleLinks[user.role] || [];

  return (
    <nav className="bg-indigo-700 text-white shadow">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/" className="font-bold text-lg">CHA</Link>
          {links.map((l) => (
            <Link key={l.to} to={l.to} className="text-sm hover:underline">
              {l.label}
            </Link>
          ))}
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm capitalize">{user.role.toLowerCase()}</span>
          <button onClick={handleLogout} className="text-sm bg-white text-indigo-700 px-3 py-1 rounded hover:bg-gray-100">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};
