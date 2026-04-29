import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await api.post('/auth/login/', form);
      const tokens = res.data;
      const profile = await api.get('/auth/profile/');
      login(tokens, profile.data);
      const roleRoutes = {
        PATIENT: '/patient',
        DOCTOR: '/doctor',
        ADMIN: '/admin',
        EMERGENCY: '/emergency',
        DEPARTMENT: '/department',
      };
      navigate(roleRoutes[profile.data.role] || '/');
    } catch (err) {
      const msg = err.response?.data?.detail
        || err.response?.data?.non_field_errors?.[0]
        || 'Invalid credentials.';
      setError(msg);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow w-full max-w-md">
        <h1 className="text-2xl font-bold mb-4 text-center">Coruscant Health Administration</h1>
        <h2 className="text-lg font-semibold mb-4 text-center">Login</h2>
        {error && <div className="bg-red-100 text-red-700 p-2 rounded mb-4">{error}</div>}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Username</label>
          <input name="username" value={form.username} onChange={handleChange} className="w-full border rounded px-3 py-2" required />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Password</label>
          <input name="password" type="password" value={form.password} onChange={handleChange} className="w-full border rounded px-3 py-2" required />
        </div>
        <button className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700">Login</button>
        <p className="mt-4 text-center text-sm">
          No account? <Link to="/register" className="text-indigo-600 hover:underline">Register</Link>
        </p>
      </form>
    </div>
  );
};

export default Login;
