import React, { useState } from 'react';
import api from '../services/api';

const EmergencyEntry = () => {
  const [form, setForm] = useState({ first_name: '', last_name: '', condition_notes: '' });
  const [message, setMessage] = useState('');
  const [submitted, setSubmitted] = useState(null);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const res = await api.post('/emergency/', form);
      setSubmitted(res.data);
      setForm({ first_name: '', last_name: '', condition_notes: '' });
      setMessage('Patient logged successfully.');
    } catch {
      setMessage('Failed to log patient.');
    }
  };

  return (
    <div className="max-w-xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-4 text-center">Emergency Quick Entry</h1>
      {message && <div className="bg-green-100 text-green-700 p-2 rounded mb-4">{message}</div>}

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">First Name</label>
          <input name="first_name" value={form.first_name} onChange={handleChange} className="w-full border rounded px-3 py-2" required />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Last Name</label>
          <input name="last_name" value={form.last_name} onChange={handleChange} className="w-full border rounded px-3 py-2" required />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Condition Notes</label>
          <textarea name="condition_notes" value={form.condition_notes} onChange={handleChange} className="w-full border rounded px-3 py-2" rows={3} />
        </div>
        <button className="w-full bg-red-600 text-white py-2 rounded hover:bg-red-700 font-semibold">
          Log Patient
        </button>
      </form>

      {submitted && (
        <div className="mt-4 bg-gray-100 p-4 rounded text-sm">
          <div className="font-semibold">Logged Patient Details</div>
          <div>ID: {submitted.id}</div>
          <div>Name: {submitted.first_name} {submitted.last_name}</div>
          <div>Arrival: {new Date(submitted.arrival_time).toLocaleString()}</div>
        </div>
      )}
    </div>
  );
};

export default EmergencyEntry;
