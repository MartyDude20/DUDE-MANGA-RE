import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from './Auth/AuthContext.jsx';
import { 
  FaArrowLeft, 
  FaSort, 
  FaSortAlphaDown, 
  FaSortAlphaUp, 
  FaClock, 
  FaStar,
  FaEdit,
  FaTrash,
  FaBook,
  FaEye,
  FaSearch,
  FaFilter
} from 'react-icons/fa';

const ReadingListDetails = () => {
  const { listId } = useParams();
  const navigate = useNavigate();
  const { authFetch } = useAuth();
  const [listData, setListData] = useState(null);
  const [mangaEntries, setMangaEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('added_at_desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [showSortMenu, setShowSortMenu] = useState(false);
  const [showSearch, setShowSearch] = useState(false);

  useEffect(() => {
    fetchListDetails();
  }, [listId, sortBy]);

  const fetchListDetails = async () => {
    try {
      setLoading(true);
      const response = await authFetch(`/api/reading-lists/${listId}?sort=${sortBy}`);
      if (response.ok) {
        const data = await response.json();
        setListData(data.list);
        setMangaEntries(data.manga_entries);
      } else {
        setError('Failed to load reading list details');
      }
    } catch (error) {
      console.error('Failed to fetch reading list details:', error);
      setError('Failed to load reading list details');
    } finally {
      setLoading(false);
    }
  };

  const handleSortChange = (newSortBy) => {
    setSortBy(newSortBy);
    setShowSortMenu(false);
  };

  const filteredManga = mangaEntries.filter(manga =>
    manga.manga_title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getSortLabel = (sortBy) => {
    switch (sortBy) {
      case 'title_asc': return 'A → Z';
      case 'title_desc': return 'Z → A';
      case 'added_at_desc': return 'Recently Added';
      case 'added_at_asc': return 'Oldest Added';
      case 'rating_desc': return 'Highest Rated';
      default: return 'Recently Added';
    }
  };

  const getSortIcon = (sortBy) => {
    switch (sortBy) {
      case 'title_asc': return <FaSortAlphaDown className="w-4 h-4" />;
      case 'title_desc': return <FaSortAlphaUp className="w-4 h-4" />;
      case 'added_at_desc': return <FaClock className="w-4 h-4" />;
      case 'added_at_asc': return <FaClock className="w-4 h-4" />;
      case 'rating_desc': return <FaStar className="w-4 h-4" />;
      default: return <FaSort className="w-4 h-4" />;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const MangaCard = ({ manga }) => (
    <div className="bg-gray-800 rounded-lg overflow-hidden border border-gray-700 hover:border-blue-500 transition-colors">
      <div className="relative">
        <img 
          src={manga.cover_url || '/placeholder-manga.jpg'} 
          alt={manga.manga_title}
          className="w-full h-48 object-cover"
          onError={(e) => {
            e.target.src = '/placeholder-manga.jpg';
          }}
        />
        {manga.rating && (
          <div className="absolute top-2 right-2 bg-yellow-500 text-black px-2 py-1 rounded-full text-xs font-bold flex items-center">
            <FaStar className="w-3 h-3 mr-1" />
            {manga.rating}
          </div>
        )}
      </div>
      
      <div className="p-4">
        <h3 className="text-white font-semibold text-lg mb-2 line-clamp-2">
          {manga.manga_title}
        </h3>
        
        <div className="flex items-center justify-between text-sm text-gray-400 mb-3">
          <span className="bg-gray-700 px-2 py-1 rounded text-xs">
            {manga.source}
          </span>
          <span>{formatDate(manga.added_at)}</span>
        </div>
        
        {manga.notes && (
          <p className="text-gray-400 text-sm mb-3 line-clamp-2">
            {manga.notes}
          </p>
        )}
        
        {manga.tags && manga.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {manga.tags.slice(0, 3).map((tag, index) => (
              <span 
                key={index}
                className="bg-blue-600 text-white text-xs px-2 py-1 rounded"
              >
                {tag}
              </span>
            ))}
            {manga.tags.length > 3 && (
              <span className="text-gray-500 text-xs">
                +{manga.tags.length - 3} more
              </span>
            )}
          </div>
        )}
        
        <div className="flex space-x-2">
          <Link 
            to={`/manga/${manga.source}/${manga.manga_id}`}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center py-2 rounded transition-colors"
          >
            <FaEye className="w-4 h-4 inline mr-1" />
            View
          </Link>
          <button className="p-2 text-gray-400 hover:text-red-400 transition-colors">
            <FaTrash className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 p-4">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-800 rounded w-1/4 mb-8"></div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {[...Array(10)].map((_, i) => (
                <div key={i} className="h-80 bg-gray-800 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 p-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <FaBook className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">Error Loading List</h3>
            <p className="text-gray-500 mb-6">{error}</p>
            <button
              onClick={() => navigate('/reading-lists')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              Back to Lists
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/reading-lists')}
                className="p-2 text-gray-400 hover:text-white transition-colors"
              >
                <FaArrowLeft className="w-5 h-5" />
              </button>
              <div className="flex items-center space-x-3">
                <div 
                  className="w-6 h-6 rounded-full"
                  style={{ backgroundColor: listData?.color }}
                ></div>
                <h1 className="text-2xl md:text-3xl font-bold text-white">
                  {listData?.name}
                </h1>
                {listData?.is_default && (
                  <span className="px-2 py-1 text-xs bg-blue-500 text-white rounded-full">
                    Default
                  </span>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Mobile Search Toggle */}
              <button
                onClick={() => setShowSearch(!showSearch)}
                className="md:hidden p-2 text-gray-400 hover:text-white transition-colors"
              >
                <FaSearch className="w-5 h-5" />
              </button>
              
              {/* Sort Menu */}
              <div className="relative">
                <button
                  onClick={() => setShowSortMenu(!showSortMenu)}
                  className="flex items-center space-x-2 bg-gray-800 hover:bg-gray-700 text-white px-3 py-2 rounded-lg transition-colors"
                >
                  {getSortIcon(sortBy)}
                  <span className="hidden sm:inline">{getSortLabel(sortBy)}</span>
                  <FaSort className="w-4 h-4" />
                </button>
                
                {showSortMenu && (
                  <div className="absolute right-0 top-full mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-10 min-w-[200px]">
                    <div className="py-2">
                      <button
                        onClick={() => handleSortChange('title_asc')}
                        className="w-full text-left px-4 py-2 text-white hover:bg-gray-700 transition-colors flex items-center space-x-2"
                      >
                        <FaSortAlphaDown className="w-4 h-4" />
                        <span>A → Z</span>
                      </button>
                      <button
                        onClick={() => handleSortChange('title_desc')}
                        className="w-full text-left px-4 py-2 text-white hover:bg-gray-700 transition-colors flex items-center space-x-2"
                      >
                        <FaSortAlphaUp className="w-4 h-4" />
                        <span>Z → A</span>
                      </button>
                      <button
                        onClick={() => handleSortChange('added_at_desc')}
                        className="w-full text-left px-4 py-2 text-white hover:bg-gray-700 transition-colors flex items-center space-x-2"
                      >
                        <FaClock className="w-4 h-4" />
                        <span>Recently Added</span>
                      </button>
                      <button
                        onClick={() => handleSortChange('added_at_asc')}
                        className="w-full text-left px-4 py-2 text-white hover:bg-gray-700 transition-colors flex items-center space-x-2"
                      >
                        <FaClock className="w-4 h-4" />
                        <span>Oldest Added</span>
                      </button>
                      <button
                        onClick={() => handleSortChange('rating_desc')}
                        className="w-full text-left px-4 py-2 text-white hover:bg-gray-700 transition-colors flex items-center space-x-2"
                      >
                        <FaStar className="w-4 h-4" />
                        <span>Highest Rated</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Description */}
          {listData?.description && (
            <p className="text-gray-400 mb-4">{listData.description}</p>
          )}
          
          {/* Stats */}
          <div className="flex items-center space-x-4 text-sm text-gray-500 mb-4">
            <span className="flex items-center space-x-1">
              <FaBook className="w-4 h-4" />
              <span>{mangaEntries.length} manga</span>
            </span>
            <span>Created {formatDate(listData?.created_at)}</span>
          </div>
          
          {/* Search Bar - Desktop */}
          <div className="hidden md:block mb-6">
            <div className="relative">
              <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search manga in this list..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
          
          {/* Search Bar - Mobile */}
          {showSearch && (
            <div className="md:hidden mb-6">
              <div className="relative">
                <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search manga..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
          )}
        </div>

        {/* Manga Grid */}
        {filteredManga.length === 0 ? (
          <div className="text-center py-12">
            <FaBook className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">
              {searchQuery ? 'No manga found' : 'No manga in this list'}
            </h3>
            <p className="text-gray-500 mb-6">
              {searchQuery 
                ? 'Try adjusting your search terms' 
                : 'Add some manga to get started'
              }
            </p>
            {!searchQuery && (
              <Link
                to="/search"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
              >
                Browse Manga
              </Link>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {filteredManga.map((manga) => (
              <MangaCard key={manga.id} manga={manga} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReadingListDetails; 