import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './Auth/AuthContext.jsx';
import { 
  FaBook, 
  FaClock, 
  FaChartLine, 
  FaStar, 
  FaEye, 
  FaBookmark, 
  FaHistory,
  FaArrowRight,
  FaCalendarAlt,
  FaTrophy,
  FaFire,
  FaSearch
} from 'react-icons/fa';

const Dashboard = () => {
  const { user, isAuthenticated, authFetch } = useAuth();
  const [recentActivity, setRecentActivity] = useState([]);
  const [continueReading, setContinueReading] = useState([]);
  const [readingStats, setReadingStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated) {
      fetchDashboardData();
    }
  }, [isAuthenticated]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Use the new single dashboard endpoint for better performance
      const response = await authFetch('/api/dashboard?activity_limit=5&continue_limit=3');
      
      if (response.ok) {
        const data = await response.json();
        setRecentActivity(data.recent_activity || []);
        setContinueReading(data.continue_reading || []);
        setReadingStats(data.reading_stats || {});
      } else {
        console.error('Failed to fetch dashboard data');
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
    return `${Math.floor(diffInHours / 168)}w ago`;
  };

  const StatCard = ({ icon: Icon, title, value, subtitle, color = 'blue' }) => (
    <div className={`bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-${color}-500 transition-colors`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
          {subtitle && <p className="text-gray-500 text-xs mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-full bg-${color}-500/10`}>
          <Icon className={`w-6 h-6 text-${color}-500`} />
        </div>
      </div>
    </div>
  );

  const MangaCard = ({ manga, type = 'activity' }) => (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-blue-500 transition-colors">
      <div className="flex space-x-4">
        <img 
          src={manga.cover_url || '/placeholder-manga.jpg'} 
          alt={manga.manga_title}
          className="w-16 h-24 object-cover rounded-md"
          onError={(e) => {
            e.target.src = '/placeholder-manga.jpg';
          }}
        />
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-medium truncate">{manga.manga_title}</h3>
          <p className="text-gray-400 text-sm truncate">{manga.chapter_title}</p>
          <div className="flex items-center space-x-2 mt-2">
            <span className="text-xs text-gray-500">{manga.source}</span>
            {type === 'activity' && (
              <span className="text-xs text-gray-500">{formatTimeAgo(manga.read_at)}</span>
            )}
            {type === 'continue' && manga.completion_percentage && (
              <div className="flex-1">
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${manga.completion_percentage}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-500 mt-1 block">
                  {Math.round(manga.completion_percentage)}% complete
                </span>
              </div>
            )}
          </div>
        </div>
        <Link 
          to={`/manga/${manga.source}/${manga.manga_id}`}
          className="text-blue-500 hover:text-blue-400 transition-colors"
        >
          <FaArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded w-1/4 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-800 rounded"></div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {[...Array(2)].map((_, i) => (
                <div key={i} className="h-64 bg-gray-800 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-gray-400">
            Continue your manga journey from where you left off
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={FaBook}
            title="Manga Read"
            value={readingStats.total_manga || 0}
            subtitle="This month"
            color="blue"
          />
          <StatCard
            icon={FaClock}
            title="Reading Time"
            value={readingStats.total_hours ? `${Math.round(readingStats.total_hours)}h` : '0h'}
            subtitle="This month"
            color="green"
          />
          <StatCard
            icon={FaChartLine}
            title="Reading Streak"
            value={readingStats.current_streak || 0}
            subtitle="days"
            color="yellow"
          />
          <StatCard
            icon={FaStar}
            title="Average Rating"
            value={readingStats.average_rating ? readingStats.average_rating.toFixed(1) : '0.0'}
            subtitle="out of 5"
            color="purple"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Continue Reading */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white flex items-center">
                <FaEye className="w-5 h-5 mr-2 text-blue-500" />
                Continue Reading
              </h2>
              <Link 
                to="/reading-progress"
                className="text-blue-500 hover:text-blue-400 text-sm font-medium"
              >
                View All
              </Link>
            </div>
            
            {continueReading.length === 0 ? (
              <div className="text-center py-8">
                <FaBook className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No manga in progress</p>
                <Link 
                  to="/search"
                  className="text-blue-500 hover:text-blue-400 text-sm font-medium mt-2 inline-block"
                >
                  Start reading something new
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {continueReading.map((manga, index) => (
                  <MangaCard key={index} manga={manga} type="continue" />
                ))}
              </div>
            )}
          </div>

          {/* Recent Activity */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white flex items-center">
                <FaHistory className="w-5 h-5 mr-2 text-green-500" />
                Recent Activity
              </h2>
              <Link 
                to="/read-history"
                className="text-blue-500 hover:text-blue-400 text-sm font-medium"
              >
                View All
              </Link>
            </div>
            
            {recentActivity.length === 0 ? (
              <div className="text-center py-8">
                <FaHistory className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No recent activity</p>
                <Link 
                  to="/search"
                  className="text-blue-500 hover:text-blue-400 text-sm font-medium mt-2 inline-block"
                >
                  Start reading to see activity
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {recentActivity.map((activity, index) => (
                  <MangaCard key={index} manga={activity} type="activity" />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center">
            <FaFire className="w-5 h-5 mr-2 text-orange-500" />
            Quick Actions
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link 
              to="/search"
              className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-lg text-center transition-colors"
            >
              <FaSearch className="w-6 h-6 mx-auto mb-2" />
              <span className="font-medium">Search Manga</span>
            </Link>
            
            <Link 
              to="/saved"
              className="bg-green-600 hover:bg-green-700 text-white p-4 rounded-lg text-center transition-colors"
            >
              <FaBookmark className="w-6 h-6 mx-auto mb-2" />
              <span className="font-medium">Saved Manga</span>
            </Link>
            
            <Link 
              to="/reading-lists"
              className="bg-purple-600 hover:bg-purple-700 text-white p-4 rounded-lg text-center transition-colors"
            >
              <FaBook className="w-6 h-6 mx-auto mb-2" />
              <span className="font-medium">Reading Lists</span>
            </Link>
            
            <Link 
              to="/achievements"
              className="bg-yellow-600 hover:bg-yellow-700 text-white p-4 rounded-lg text-center transition-colors"
            >
              <FaTrophy className="w-6 h-6 mx-auto mb-2" />
              <span className="font-medium">Achievements</span>
            </Link>
          </div>
        </div>

        {/* Reading Goals */}
        {readingStats.goals && (
          <div className="mt-8 bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center">
              <FaCalendarAlt className="w-5 h-5 mr-2 text-indigo-500" />
              Reading Goals
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {readingStats.goals.map((goal, index) => (
                <div key={index} className="bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-white font-medium">{goal.title}</h3>
                    <span className="text-sm text-gray-400">{goal.progress}/{goal.target}</span>
                  </div>
                  <div className="w-full bg-gray-600 rounded-full h-2">
                    <div 
                      className="bg-indigo-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min((goal.progress / goal.target) * 100, 100)}%` }}
                    ></div>
                  </div>
                  <p className="text-gray-400 text-sm mt-2">{goal.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 