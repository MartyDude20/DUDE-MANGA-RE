import React, { useState, useEffect } from 'react';
import { useAuth } from './Auth/AuthContext.jsx';
import { FaPlus, FaTimes, FaBook, FaCheck } from 'react-icons/fa';

const ReadingListPopup = ({ isOpen, onClose, manga, onSuccess }) => {
  const { authFetch, isAuthenticated } = useAuth();
  const [lists, setLists] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedList, setSelectedList] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newList, setNewList] = useState({ name: '', description: '', color: '#3B82F6' });
  const [creatingList, setCreatingList] = useState(false);
  const [addingToList, setAddingToList] = useState(false);

  useEffect(() => {
    if (isOpen && isAuthenticated) {
      fetchReadingLists();
    }
  }, [isOpen, isAuthenticated]);

  const fetchReadingLists = async () => {
    try {
      setLoading(true);
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
      setCreatingList(true);
      const response = await authFetch('/api/reading-lists', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newList),
      });

      if (response.ok) {
        const data = await response.json();
        setShowCreateForm(false);
        setNewList({ name: '', description: '', color: '#3B82F6' });
        await fetchReadingLists();
        // Auto-select the newly created list
        setSelectedList(data.list.id);
      }
    } catch (error) {
      console.error('Failed to create reading list:', error);
    } finally {
      setCreatingList(false);
    }
  };

  const addMangaToList = async (listId) => {
    if (!manga) return;
    
    try {
      setAddingToList(true);
      const response = await authFetch(`/api/reading-lists/${listId}/manga`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          manga_id: manga.id,
          source: manga.source,
          manga_title: manga.title,
          cover_url: manga.image,
        }),
      });

      if (response.ok) {
        onSuccess && onSuccess(listId);
        onClose();
        // Show success message
        const successMessage = document.createElement('div');
        successMessage.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        successMessage.textContent = 'Manga added to list successfully!';
        document.body.appendChild(successMessage);
        setTimeout(() => {
          document.body.removeChild(successMessage);
        }, 3000);
      } else {
        const errorData = await response.json();
        alert(errorData.error || 'Failed to add manga to list');
      }
    } catch (error) {
      console.error('Failed to add manga to list:', error);
      alert('Failed to add manga to list');
    } finally {
      setAddingToList(false);
    }
  };

  const handleListSelect = (listId) => {
    setSelectedList(listId);
    addMangaToList(listId);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Add to Reading List</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <FaTimes className="w-5 h-5" />
          </button>
        </div>

        {!isAuthenticated ? (
          <div className="text-center py-8">
            <FaBook className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 mb-4">Please log in to use reading lists</p>
            <button
              onClick={onClose}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        ) : (
          <>
            {showCreateForm ? (
              <div>
                <h3 className="text-lg font-medium text-white mb-4">Create New List</h3>
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
                      disabled={creatingList}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-2 rounded-lg transition-colors"
                    >
                      {creatingList ? 'Creating...' : 'Create List'}
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
            ) : (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-white">Select a List</h3>
                  <button
                    onClick={() => setShowCreateForm(true)}
                    className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-lg transition-colors text-sm"
                  >
                    <FaPlus className="w-3 h-3" />
                    <span>New List</span>
                  </button>
                </div>

                {loading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="text-gray-400 mt-2">Loading lists...</p>
                  </div>
                ) : lists.length === 0 ? (
                  <div className="text-center py-8">
                    <FaBook className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400 mb-4">No reading lists yet</p>
                    <button
                      onClick={() => setShowCreateForm(true)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      Create Your First List
                    </button>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {lists.map((list) => (
                      <button
                        key={list.id}
                        onClick={() => handleListSelect(list.id)}
                        disabled={addingToList}
                        className="w-full flex items-center justify-between p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <div className="flex items-center space-x-3">
                          <div 
                            className="w-4 h-4 rounded-full"
                            style={{ backgroundColor: list.color }}
                          ></div>
                          <div className="text-left">
                            <p className="text-white font-medium">{list.name}</p>
                            <p className="text-gray-400 text-sm">{list.manga_count || 0} manga</p>
                          </div>
                        </div>
                        {addingToList && selectedList === list.id && (
                          <FaCheck className="w-4 h-4 text-green-400" />
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ReadingListPopup; 