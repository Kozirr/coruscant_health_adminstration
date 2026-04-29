import React, { useEffect, useState } from 'react';
import api from '../services/api';

const DepartmentOrders = () => {
  const [orders, setOrders] = useState([]);
  const [filter, setFilter] = useState('PENDING');
  const [message, setMessage] = useState('');
  const [completingId, setCompletingId] = useState(null);
  const [resultNotes, setResultNotes] = useState('');
  const [resultFile, setResultFile] = useState(null);

  useEffect(() => {
    fetchOrders();
  }, [filter]);

  const fetchOrders = async () => {
    try {
      const res = await api.get(`/orders/?status=${filter}`);
      setOrders(res.data.results || res.data);
    } catch {}
  };

  const executeOrder = async (id, status) => {
    try {
      await api.patch(`/orders/${id}/execute/`, { status });
      setMessage(`Order marked ${status}.`);
      fetchOrders();
    } catch {
      setMessage('Failed to update order.');
    }
  };

  const completeOrder = async (id) => {
    try {
      const formData = new FormData();
      formData.append('status', 'COMPLETED');
      if (resultNotes) formData.append('result_notes', resultNotes);
      if (resultFile) formData.append('result_file', resultFile);
      await api.patch(`/orders/${id}/execute/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage('Order completed with results.');
      setCompletingId(null);
      setResultNotes('');
      setResultFile(null);
      fetchOrders();
    } catch {
      setMessage('Failed to complete order.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-4">Department Orders</h1>
      {message && <div className="bg-green-100 text-green-700 p-2 rounded mb-4">{message}</div>}

      <div className="flex gap-2 mb-4">
        {['PENDING', 'IN_PROGRESS', 'COMPLETED'].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1 rounded text-sm font-medium ${filter === s ? 'bg-indigo-600 text-white' : 'bg-white text-gray-700 border'}`}
          >
            {s.replace('_', ' ')}
          </button>
        ))}
      </div>

      <div className="bg-white rounded shadow overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2">ID</th>
              <th className="px-4 py-2">Patient</th>
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Created</th>
              <th className="px-4 py-2">Results</th>
              <th className="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {orders.map((o) => (
              <tr key={o.id} className="hover:bg-gray-50">
                <td className="px-4 py-2">{o.id}</td>
                <td className="px-4 py-2">{o.patient_name}</td>
                <td className="px-4 py-2">{o.order_type.replace('_', ' ')}</td>
                <td className="px-4 py-2 capitalize">{o.status.replace('_', ' ').toLowerCase()}</td>
                <td className="px-4 py-2">{new Date(o.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-2 max-w-xs">
                  {o.result_notes ? (
                    <div className="text-xs text-gray-700">{o.result_notes}</div>
                  ) : (
                    <span className="text-xs text-gray-400">—</span>
                  )}
                  {o.result_file && (
                    <div className="mt-1">
                      <a
                        href={o.result_file}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-indigo-600 hover:underline"
                      >
                        Download result
                      </a>
                    </div>
                  )}
                </td>
                <td className="px-4 py-2">
                  {o.status === 'PENDING' && (
                    <button onClick={() => executeOrder(o.id, 'IN_PROGRESS')} className="text-indigo-600 hover:underline text-sm">Start</button>
                  )}
                  {o.status === 'IN_PROGRESS' && (
                    <>
                      {completingId === o.id ? (
                        <div className="flex flex-col gap-2">
                          <textarea
                            className="border rounded px-2 py-1 text-xs w-48"
                            placeholder="Result notes"
                            value={resultNotes}
                            onChange={(e) => setResultNotes(e.target.value)}
                          />
                          <input
                            type="file"
                            className="text-xs"
                            onChange={(e) => setResultFile(e.target.files[0])}
                          />
                          <div className="flex gap-2">
                            <button
                              onClick={() => completeOrder(o.id)}
                              className="text-green-600 hover:underline text-xs"
                            >
                              Submit
                            </button>
                            <button
                              onClick={() => { setCompletingId(null); setResultNotes(''); setResultFile(null); }}
                              className="text-gray-500 hover:underline text-xs"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={() => setCompletingId(o.id)}
                          className="text-green-600 hover:underline text-sm"
                        >
                          Complete
                        </button>
                      )}
                    </>
                  )}
                </td>
              </tr>
            ))}
            {orders.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-4 text-center text-gray-500">No orders found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DepartmentOrders;
