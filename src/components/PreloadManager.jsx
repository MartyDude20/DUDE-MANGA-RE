import React, { useState, useEffect } from 'react';
import { useAuth } from './Auth/AuthContext.jsx';

const PreloadManager = () => {
  const { authFetch, user } = useAuth();
  
  // Check if user is admin
  if (!user?.hasAdmin) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-4">Access Denied</h1>
          <p className="text-gray-300">You need admin privileges to access the Preload Manager.</p>
        </div>
      </div>
    );
  }
  const [stats, setStats] = useState({});
  const [jobs, setJobs] = useState([]);
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('status');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Load status
      const statusResponse = await authFetch('http://localhost:5000/preload/status');
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setStatus(statusData);
      }

      // Load stats
      const statsResponse = await authFetch('http://localhost:5000/preload/stats?days=7');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Load recent jobs
      const jobsResponse = await authFetch('http://localhost:5000/preload/jobs?status=pending&limit=20');
      if (jobsResponse.ok) {
        const jobsData = await jobsResponse.json();
        setJobs(jobsData);
      }
    } catch (err) {
      setError('Failed to load preload data');
      console.error('Error loading preload data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleWorkerAction = async (action) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authFetch(`http://localhost:5000/preload/${action}-worker`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        loadData(); // Refresh data
      } else {
        const errorData = await response.json();
        setError(errorData.error || `Failed to ${action} worker`);
      }
    } catch (err) {
      setError(`Failed to ${action} worker`);
      console.error(`Error ${action}ing worker:`, err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDailyJobs = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authFetch('http://localhost:5000/preload/create-daily', {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        loadData(); // Refresh data
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to create daily jobs');
      }
    } catch (err) {
      setError('Failed to create daily jobs');
      console.error('Error creating daily jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCleanup = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authFetch('http://localhost:5000/preload/cleanup?days=7', {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        loadData(); // Refresh data
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to cleanup jobs');
      }
    } catch (err) {
      setError('Failed to cleanup jobs');
      console.error('Error cleaning up jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRobots = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await authFetch('http://localhost:5000/preload/update-robots', {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        alert(result.message);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to update robots.txt');
      }
    } catch (err) {
      setError('Failed to update robots.txt');
      console.error('Error updating robots.txt:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'failed': return 'text-red-600';
      case 'running': return 'text-blue-600';
      case 'pending': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return '✅';
      case 'failed': return '❌';
      case 'running': return '🔄';
      case 'pending': return '⏳';
      default: return '❓';
    }
  };

  if (loading && Object.keys(stats).length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white mb-2">Preload Manager</h1>
        <p className="text-gray-300">
          Manage daily preloading of manga data with respectful rate limiting and robots.txt compliance.
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-900 border border-red-600 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-200">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'status', label: 'Status', icon: '📊' },
            { id: 'stats', label: 'Statistics', icon: '📈' },
            { id: 'jobs', label: 'Jobs', icon: '⚙️' },
            { id: 'actions', label: 'Actions', icon: '🔧' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Status Tab */}
      {activeTab === 'status' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      status.worker_running ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      {status.worker_running ? '🟢' : '🔴'}
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Worker Status</dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {status.worker_running ? 'Running' : 'Stopped'}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center">
                      ⏳
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Pending Jobs</dt>
                      <dd className="text-lg font-medium text-gray-900">{status.pending_jobs || 0}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                      ✅
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Completed Today</dt>
                      <dd className="text-lg font-medium text-gray-900">{status.completed_today || 0}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
                      ❌
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Failed Today</dt>
                      <dd className="text-lg font-medium text-gray-900">{status.failed_today || 0}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Quick Actions</h3>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => handleWorkerAction(status.worker_running ? 'stop' : 'start')}
                  disabled={loading}
                  className={`px-4 py-2 rounded-md text-sm font-medium ${
                    status.worker_running
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  } disabled:opacity-50`}
                >
                  {loading ? '...' : (status.worker_running ? 'Stop Worker' : 'Start Worker')}
                </button>
                
                <button
                  onClick={handleCreateDailyJobs}
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium disabled:opacity-50"
                >
                  {loading ? '...' : 'Create Daily Jobs'}
                </button>
                
                <button
                  onClick={handleUpdateRobots}
                  disabled={loading}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md text-sm font-medium disabled:opacity-50"
                >
                  {loading ? '...' : 'Update Robots.txt'}
                </button>
                
                <button
                  onClick={loadData}
                  disabled={loading}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md text-sm font-medium disabled:opacity-50"
                >
                  {loading ? '...' : 'Refresh Data'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Statistics Tab */}
      {activeTab === 'stats' && (
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Preload Statistics (Last 7 Days)</h3>
              
              {Object.keys(stats).length === 0 ? (
                <p className="text-gray-500">No statistics available yet.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Jobs</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Success Rate</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Response Time</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {Object.entries(stats).map(([key, stat]) => (
                        <tr key={key}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {stat.source}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {stat.job_type}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {stat.total_jobs}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            <span className={`font-medium ${
                              stat.success_rate >= 90 ? 'text-green-600' :
                              stat.success_rate >= 70 ? 'text-yellow-600' : 'text-red-600'
                            }`}>
                              {stat.success_rate.toFixed(1)}%
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {stat.avg_response_time ? `${stat.avg_response_time.toFixed(2)}s` : 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Jobs Tab */}
      {activeTab === 'jobs' && (
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Jobs</h3>
                <button
                  onClick={handleCleanup}
                  disabled={loading}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm font-medium disabled:opacity-50"
                >
                  {loading ? '...' : 'Cleanup Old Jobs'}
                </button>
              </div>
              
              {jobs.length === 0 ? (
                <p className="text-gray-500">No jobs found.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Target</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Scheduled</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {jobs.map((job) => (
                        <tr key={job.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                              {getStatusIcon(job.status)} {job.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {job.job_type}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {job.source}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                            {job.target_id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDate(job.scheduled_at)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {job.priority}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Actions Tab */}
      {activeTab === 'actions' && (
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Preload Actions</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="text-md font-medium text-gray-900 mb-2">Worker Control</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Start or stop the preload worker that processes background jobs.
                  </p>
                  <div className="space-y-2">
                    <button
                      onClick={() => handleWorkerAction('start')}
                      disabled={loading || status.worker_running}
                      className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-medium disabled:opacity-50"
                    >
                      Start Worker
                    </button>
                    <button
                      onClick={() => handleWorkerAction('stop')}
                      disabled={loading || !status.worker_running}
                      className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm font-medium disabled:opacity-50"
                    >
                      Stop Worker
                    </button>
                  </div>
                </div>

                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="text-md font-medium text-gray-900 mb-2">Job Management</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Create daily preload jobs and cleanup old completed jobs.
                  </p>
                  <div className="space-y-2">
                    <button
                      onClick={handleCreateDailyJobs}
                      disabled={loading}
                      className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium disabled:opacity-50"
                    >
                      Create Daily Jobs
                    </button>
                    <button
                      onClick={handleCleanup}
                      disabled={loading}
                      className="w-full px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-md text-sm font-medium disabled:opacity-50"
                    >
                      Cleanup Old Jobs
                    </button>
                  </div>
                </div>

                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="text-md font-medium text-gray-900 mb-2">Robots.txt Management</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Update robots.txt cache for all sources to ensure respectful crawling.
                  </p>
                  <button
                    onClick={handleUpdateRobots}
                    disabled={loading}
                    className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-md text-sm font-medium disabled:opacity-50"
                  >
                    Update Robots.txt
                  </button>
                </div>

                <div className="border border-gray-200 rounded-lg p-4">
                  <h4 className="text-md font-medium text-gray-900 mb-2">Data Refresh</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Refresh all preload data including status, stats, and jobs.
                  </p>
                  <button
                    onClick={loadData}
                    disabled={loading}
                    className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md text-sm font-medium disabled:opacity-50"
                  >
                    Refresh Data
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PreloadManager; 