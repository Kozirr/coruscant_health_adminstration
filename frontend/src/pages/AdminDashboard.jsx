import React, { useEffect, useState } from 'react';
import api from '../services/api';

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [stats, setStats] = useState({ total_users: 0, patients: 0, doctors: 0, orders: 0 });
  const [message, setMessage] = useState('');
  const [system, setSystem] = useState(null);

  useEffect(() => {
    fetchUsers();
    fetchStats();
    fetchSystem();
  }, []);

  const fetchUsers = async () => {
    try {
      const res = await api.get('/auth/users/');
      setUsers(res.data.results || res.data);
    } catch {}
  };

  const fetchStats = async () => {
    try {
      const u = await api.get('/auth/users/');
      const all = u.data.results || u.data;
      const p = await api.get('/patients/');
      const o = await api.get('/orders/');
      setStats({
        total_users: all.length,
        patients: all.filter((x) => x.role === 'PATIENT').length,
        doctors: all.filter((x) => x.role === 'DOCTOR').length,
        orders: (o.data.results || o.data).length,
      });
    } catch {}
  };

  const fetchSystem = async () => {
    try {
      const res = await api.get('/admin/system/');
      setSystem(res.data);
    } catch {}
  };

  const approveUser = async (id) => {
    try {
      await api.post(`/auth/users/${id}/approve/`);
      setMessage('User approved successfully.');
      fetchUsers();
    } catch {
      setMessage('Failed to approve user.');
    }
  };

  const filteredUsers = users.filter((u) => {
    if (filter === 'PENDING') return !u.is_approved;
    if (filter === 'APPROVED') return u.is_approved;
    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-4">Administrator Dashboard</h1>
      {message && <div className="bg-green-100 text-green-700 p-2 rounded mb-4">{message}</div>}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded shadow text-center">
          <div className="text-3xl font-bold text-indigo-600">{stats.total_users}</div>
          <div className="text-sm text-gray-500">Total Users</div>
        </div>
        <div className="bg-white p-4 rounded shadow text-center">
          <div className="text-3xl font-bold text-green-600">{stats.patients}</div>
          <div className="text-sm text-gray-500">Patients</div>
        </div>
        <div className="bg-white p-4 rounded shadow text-center">
          <div className="text-3xl font-bold text-blue-600">{stats.doctors}</div>
          <div className="text-sm text-gray-500">Doctors</div>
        </div>
        <div className="bg-white p-4 rounded shadow text-center">
          <div className="text-3xl font-bold text-orange-600">{stats.orders}</div>
          <div className="text-sm text-gray-500">Orders</div>
        </div>
      </div>

      {system && (
        <div className="bg-white rounded shadow p-4 mb-6">
          <h2 className="font-semibold mb-2">System Health</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${system.migrations_ok ? 'bg-green-500' : 'bg-yellow-500'}`}></span>
              <span className="text-sm text-gray-700">{system.migrations_status}</span>
            </div>
            <div className="text-sm text-gray-700">Django {system.django_version}</div>
            <div className="text-sm text-gray-700">Python {system.python_version}</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Migrations are applied automatically during Railway deployment via railway.toml.
          </p>
        </div>
      )}

      <div className="flex gap-2 mb-4">
        {['ALL', 'PENDING', 'APPROVED'].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1 rounded text-sm font-medium ${filter === s ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 border'}`}
          >
            {s === 'ALL' ? 'All Users' : s === 'PENDING' ? 'Pending Approval' : 'Approved'}
          </button>
        ))}
      </div>

      <div className="bg-white rounded shadow overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2">ID</th>
              <th className="px-4 py-2">Username</th>
              <th className="px-4 py-2">Name</th>
              <th className="px-4 py-2">Role</th>
              <th className="px-4 py-2">Email</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Joined</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {filteredUsers.map((u) => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-4 py-2">{u.id}</td>
                <td className="px-4 py-2">{u.username}</td>
                <td className="px-4 py-2">{u.first_name} {u.last_name}</td>
                <td className="px-4 py-2 capitalize">{u.role.toLowerCase()}</td>
                <td className="px-4 py-2">{u.email}</td>
                <td className="px-4 py-2">
                  <span className={`text-xs font-semibold px-2 py-1 rounded ${u.is_approved ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-800'}`}>
                    {u.is_approved ? 'Approved' : 'Pending'}
                  </span>
                </td>
                <td className="px-4 py-2">{new Date(u.date_joined).toLocaleDateString()}</td>
                <td className="px-4 py-2">
                  {!u.is_approved && (
                    <button
                      onClick={() => approveUser(u.id)}
                      className="text-indigo-600 hover:underline text-sm"
                    >
                      Approve
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {filteredUsers.length === 0 && (
              <tr>
                <td colSpan={8} className="px-4 py-4 text-center text-gray-500">No users found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminDashboard;
