import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './Auth/AuthContext.jsx';
import { 
  FaPlus, 
  FaEdit, 
  FaTrash, 
  FaBook, 
  FaEye,
  FaStar,
  FaTag
} from 'react-icons/fa';

const ReadingLists = () => {
  const { authFetch } = useAuth();
  const [lists, setLists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newList, setNewList] = useState({ name: '', description: '', color: '#3B82F6' });

  useEffect(() => {
    fetchReadingLists();
  }, []);

  const fetchReadingLists = async () => {
    try {
      const response = await authFetch('/api/reading-lists');
      if (response.ok) {
        const data = await response.json();
        setLists(data);
      }
    } catch (error) {
      console.error('Failed to fetch reading lists:', error);
    } finally {
      setLoading(false);
    }
  };

  const createList = async (e) => {
    e.preventDefault();
    try {
      const response = await authFetch('/api/reading-lists', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newList),
      });

      if (response.ok) {
        setShowCreateForm(false);
        setNewList({ name: '', description: '', color: '#3B82F6' });
        fetchReadingLists();
      }
    } catch (error) {
      console.error('Failed to create reading list:', error);
    }
  };

  const ListCard = ({ list }) => (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-blue-500 transition-colors">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div 
            className="w-4 h-4 rounded-full"
            style={{ backgroundColor: list.color }}
          ></div>
          <h3 className="text-xl font-semibold text-white">{list.name}</h3>
          {list.is_default && (
            <span className="px-2 py-1 text-xs bg-blue-500 text-white rounded-full">
              Default
            </span>
          )}
        </div>
        <div className="flex space-x-2">
          <button className="p-2 text-gray-400 hover:text-white transition-colors">
            <FaEdit className="w-4 h-4" />
          </button>
          {!list.is_default && (
            <button className="p-2 text-gray-400 hover:text-red-400 transition-colors">
              <FaTrash className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
      
      <p className="text-gray-400 mb-4">{list.description}</p>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <span className="flex items-center space-x-1">
            <FaBook className="w-4 h-4" />
            <span>{list.manga_count || 0} manga</span>
          </span>
          <span>{new Date(list.created_at).toLocaleDateString()}</span>
        </div>
        
        <Link 
          to={`/reading-lists/${list.id}`}
          className="flex items-center space-x-2 text-blue-500 hover:text-blue-400 transition-colors"
        >
          <FaEye className="w-4 h-4" />
          <span>View</span>
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-48 bg-gray-800 rounded"></div>
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
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Reading Lists</h1>
            <p className="text-gray-400">Organize your manga collection</p>
          </div>
          <button
            onClick={() => setShowCreateForm(true)}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <FaPlus className="w-4 h-4" />
            <span>New List</span>
          </button>
        </div>

        {/* Create List Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
              <h2 className="text-xl font-semibold text-white mb-4">Create New List</h2>
              <form onSubmit={createList}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      List Name
                    </label>
                    <input
                      type="text"
                      value={newList.name}
                      onChange={(e) => setNewList({ ...newList, name: e.target.value })}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                      placeholder="Enter list name"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Description
                    </label>
                    <textarea
                      value={newList.description}
                      onChange={(e) => setNewList({ ...newList, description: e.target.value })}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                      placeholder="Enter description"
                      rows="3"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Color
                    </label>
                    <input
                      type="color"
                      value={newList.color}
                      onChange={(e) => setNewList({ ...newList, color: e.target.value })}
                      className="w-full h-10 bg-gray-700 border border-gray-600 rounded-lg cursor-pointer"
                    />
                  </div>
                </div>
                <div className="flex space-x-3 mt-6">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors"
                  >
                    Create List
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Reading Lists Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {lists.map((list) => (
            <ListCard key={list.id} list={list} />
          ))}
        </div>

        {lists.length === 0 && (
          <div className="text-center py-12">
            <FaBook className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">No reading lists yet</h3>
            <p className="text-gray-500 mb-6">Create your first reading list to start organizing your manga</p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Create Your First List
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReadingLists; 