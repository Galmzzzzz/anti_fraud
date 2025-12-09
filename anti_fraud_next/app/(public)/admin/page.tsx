"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

interface TotalSent {
  phone_number: number;
  total_sent: number;
}

export default function AdminPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [totalSent, setTotalSent] = useState<TotalSent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function fetchData() {
      try {
        const meRes = await axios.get("http://localhost:8000/me", { withCredentials: true });

        const isAdminFromServer =
          meRes.data.is_admin === true ||
          meRes.data.is_admin === 1 ||
          meRes.data.is_admin === "true";

        if (!isAdminFromServer) {
          if (mounted) router.replace("/");
          return;
        }

        if (mounted) setIsAdmin(true);

        const txRes = await axios.get("http://localhost:8000/total_sent", { withCredentials: true });
        if (mounted) setTotalSent(txRes.data);

      } catch (err: any) {
        if (mounted) {
          setError("Failed to fetch data. Redirecting to login...");
          router.replace("/login");
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    fetchData();

    return () => { mounted = false };
  }, [router]);

  const handleDeleteFraud = async () => {
    try {
      setDeleting(true);
      await axios.delete("http://localhost:8000/fraud_reports", { withCredentials: true });
      alert("All fraud reports deleted!");
    } catch (err) {
      alert("Failed to delete fraud reports.");
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-blue-700 font-medium">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex items-center justify-center p-6">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Error</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.push("/login")}
            className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition duration-200"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex items-center justify-center p-6">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
          <div className="text-red-500 text-4xl mb-4">🔒</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-6">You don't have permission to access this page.</p>
          <button
            onClick={() => router.push("/")}
            className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition duration-200"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const totalTransactions = totalSent.reduce((sum, item) => sum + item.total_sent, 0);
  const uniqueUsers = totalSent.length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600 mt-2">Monitor and manage user transactions</p>
            </div>
            <button
              onClick={() => router.push("/")}
              className="px-6 py-3 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition duration-200 shadow-sm"
            >
              Back to Home
            </button>
          </div>
        </header>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Total Users</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{uniqueUsers}</p>
              </div>
              <div className="bg-blue-100 p-3 rounded-full">
                <span className="text-blue-600 text-2xl">👤</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Total Sent</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">${totalTransactions.toLocaleString()}</p>
              </div>
              <div className="bg-blue-100 p-3 rounded-full">
                <span className="text-blue-600 text-2xl">💰</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm font-medium">Average per User</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  ${uniqueUsers > 0 ? Math.round(totalTransactions / uniqueUsers).toLocaleString() : 0}
                </p>
              </div>
              <div className="bg-blue-100 p-3 rounded-full">
                <span className="text-blue-600 text-2xl">📊</span>
              </div>
            </div>
          </div>
        </div>

        {/* Transactions Table */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Transaction Summary by User</h2>
            <p className="text-gray-600 text-sm mt-1">List of all users and their total sent amounts</p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Phone Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Total Sent ($)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {totalSent.length > 0 ? (
                  totalSent.map((item, index) => (
                    <tr key={index} className="hover:bg-blue-50 transition duration-150">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-blue-600 font-medium">U{index + 1}</span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{item.phone_number}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-lg font-bold text-gray-900">${item.total_sent.toLocaleString()}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 text-xs font-semibold rounded-full ${item.total_sent > 500 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                          {item.total_sent > 500 ? 'High Activity' : 'Normal'}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={3} className="px-6 py-12 text-center">
                      <div className="text-gray-400 text-lg">No transaction data available</div>
                      <p className="text-gray-500 mt-2">Transaction records will appear here</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {totalSent.length > 0 && (
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-600">
                  Showing <span className="font-semibold">{totalSent.length}</span> users
                </div>
                <div className="text-sm text-gray-600">
                  Total: <span className="font-semibold">${totalTransactions.toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Admin Actions */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Admin Actions</h2>
          <p className="text-gray-600 mb-6">
            This action will permanently delete all fraud reports. This operation cannot be undone.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={handleDeleteFraud}
              disabled={deleting}
              className={`px-6 py-3 font-medium rounded-lg transition duration-200 flex-1 ${deleting 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-red-600 hover:bg-red-700 text-white'}`}
            >
              {deleting ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Deleting...
                </div>
              ) : (
                'Delete All Fraud Reports'
              )}
            </button>
            
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition duration-200 flex-1"
            >
              Refresh Data
            </button>
          </div>
          
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <span className="text-yellow-600 text-xl">⚠️</span>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">Warning</h3>
                <div className="mt-1 text-sm text-yellow-700">
                  <p>Administrative actions affect all users. Please proceed with caution.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-8 text-center text-gray-500 text-sm">
          <p>Admin Dashboard • {new Date().getFullYear()} • Secure Transaction System</p>
        </footer>
      </div>
    </div>
  );
}