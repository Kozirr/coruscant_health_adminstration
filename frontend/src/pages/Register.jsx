import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

const Register = () => {
  const [form, setForm] = useState({
    username: '', password: '', email: '', first_name: '', last_name: '', role: 'PATIENT', phone: ''
  });
  const [error, setError] = useState('');
  const [pendingMsg, setPendingMsg] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setPendingMsg('');
    try {
      const res = await api.post('/auth/register/', form);
      const user = res.data?.user;
      if (user && user.is_approved === false) {
        setPendingMsg('Registration submitted. Your account is pending administrator approval.');
      } else {
        navigate('/login');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded shadow w-full max-w-md">
        <h1 className="text-2xl font-bold mb-4 text-center">Register</h1>
        {error && <div className="bg-red-100 text-red-700 p-2 rounded mb-4">{error}</div>}
        {pendingMsg && <div className="bg-yellow-100 text-yellow-800 p-2 rounded mb-4">{pendingMsg}</div>}
        <div className="mb-3">
          <label className="block text-sm font-medium mb-1">Username</label>
          <input name="username" value={form.username} onChange={handleChange} className="w-full border rounded px-3 py-2" required />
        </div>
        <div className="mb-3">
          <label className="block text-sm font-medium mb-1">Password</label>
          <input name="password" type="password" value={form.password} onChange={handleChange} className="w-full border rounded px-3 py-2" required minLength={8} />
        </div>
        <div className="mb-3">
          <label className="block text-sm font-medium mb-1">Email</label>
          <input name="email" type="email" value={form.email} onChange={handleChange} className="w-full border rounded px-3 py-2" required />
        </div>
        <div className="mb-3 grid grid-cols-2 gap-2">
          <div>
            <label className="block text-sm font-medium mb-1">First Name</label>
            <input name="first_name" value={form.first_name} onChange={handleChange} className="w-full border rounded px-3 py-2" required />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Last Name</label>
            <input name="last_name" value={form.last_name} onChange={handleChange} className="w-full border rounded px-3 py-2" required />
          </div>
        </div>
        <div className="mb-3">
          <label className="block text-sm font-medium mb-1">Role</label>
          <select name="role" value={form.role} onChange={handleChange} className="w-full border rounded px-3 py-2">
            <option value="PATIENT">Patient</option>
            <option value="DOCTOR">Doctor</option>
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Phone</label>
          <input name="phone" value={form.phone} onChange={handleChange} className="w-full border rounded px-3 py-2" />
        </div>
        <button className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700">Register</button>
        <p className="mt-4 text-center text-sm">
          Already have an account? <Link to="/login" className="text-indigo-600 hover:underline">Login</Link>
        </p>
      </form>
    </div>
  );
};

export default Register;
