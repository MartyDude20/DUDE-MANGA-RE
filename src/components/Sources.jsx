import React, { useState, useEffect } from 'react';

const SOURCE_OPTIONS = [
  { 
    id: 'weebcentral', 
    name: 'WeebCentral', 
    description: 'Popular manga source with a wide variety of titles',
    enabled: true 
  },
  { 
    id: 'asurascans', 
    name: 'Asura Scans', 
    description: 'High-quality manga translations and releases',
    enabled: true 
  },
];

const Sources = () => {
  const [sources, setSources] = useState(SOURCE_OPTIONS);
  const [saved, setSaved] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortOrder, setSortOrder] = useState('az'); // 'az' or 'za'

  // Load saved sources from localStorage on component mount
  useEffect(() => {
    const savedSources = localStorage.getItem('mangaSources');
    if (savedSources) {
      setSources(JSON.parse(savedSources));
    }
  }, []);

  const handleSourceToggle = (sourceId) => {
    setSources(prevSources => 
      prevSources.map(source => 
        source.id === sourceId 
          ? { ...source, enabled: !source.enabled }
          : source
      )
    );
    setSaved(false);
  };

  const handleSave = () => {
    localStorage.setItem('mangaSources', JSON.stringify(sources));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  // Filter sources based on search query
  let filteredSources = sources.filter(source => 
    (source.name && source.name.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (source.description && source.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Sort sources by name
  filteredSources = filteredSources.sort((a, b) => {
    if (!a.name || !b.name) return 0;
    if (sortOrder === 'az') {
      return a.name.localeCompare(b.name);
    } else {
      return b.name.localeCompare(a.name);
    }
  });

  const enabledCount = sources.filter(source => source.enabled).length;
  const filteredEnabledCount = filteredSources.filter(source => source.enabled).length;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-4">Manga Sources</h1>
        <p className="text-gray-300 mb-6">
          Enable or disable manga sources to customize your search results. 
          Currently {enabledCount} of {sources.length} sources are enabled.
        </p>
        
        {/* Search Bar */}
        <div className="mb-6">
          <div className="relative mb-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search sources by name or description..."
              className="w-full px-4 py-3 pl-10 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-800 text-white placeholder-gray-400"
            />
            <svg 
              className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <div className="flex items-center gap-2 mb-2">
            <button
              type="button"
              className={`px-3 py-1 rounded text-sm font-medium border focus:outline-none transition-colors ${sortOrder === 'az' ? 'bg-blue-600 text-white border-blue-700' : 'bg-gray-700 text-gray-200 border-gray-600 hover:bg-gray-600'}`}
              onClick={() => setSortOrder('az')}
            >
              Sort A-Z
            </button>
            <button
              type="button"
              className={`px-3 py-1 rounded text-sm font-medium border focus:outline-none transition-colors ${sortOrder === 'za' ? 'bg-blue-600 text-white border-blue-700' : 'bg-gray-700 text-gray-200 border-gray-600 hover:bg-gray-600'}`}
              onClick={() => setSortOrder('za')}
            >
              Sort Z-A
            </button>
          </div>
          {searchQuery && (
            <p className="text-sm text-gray-400 mt-2">
              Showing {filteredSources.length} of {sources.length} sources 
              ({filteredEnabledCount} enabled)
            </p>
          )}
        </div>
        
        <div className="flex items-center justify-between mb-6">
          <div className="flex space-x-4">
            <button
              onClick={() => setSources(prev => prev.map(s => ({ ...s, enabled: true })))}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Enable All
            </button>
            <button
              onClick={() => setSources(prev => prev.map(s => ({ ...s, enabled: false })))}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Disable All
            </button>
          </div>
          
          <button
            onClick={handleSave}
            className={`px-6 py-2 rounded-lg transition-colors ${
              saved 
                ? 'bg-green-600 text-white' 
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {saved ? 'Saved!' : 'Save Changes'}
          </button>
        </div>
      </div>

      {filteredSources.length === 0 ? (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-400 mb-2">No sources found</h3>
          <p className="text-gray-500">Try adjusting your search terms</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredSources.map((source) => (
            <div 
              key={source.id} 
              className={`p-6 rounded-lg border transition-all ${
                source.enabled 
                  ? 'bg-gray-800 border-gray-600' 
                  : 'bg-gray-900 border-gray-700 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-xl font-semibold text-white">{source.name}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      source.enabled 
                        ? 'bg-green-900 text-green-200' 
                        : 'bg-red-900 text-red-200'
                    }`}>
                      {source.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                  <p className="text-gray-300">{source.description}</p>
                </div>
                
                <div className="flex items-center space-x-4">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={source.enabled}
                      onChange={() => handleSourceToggle(source.id)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {enabledCount === 0 && (
        <div className="mt-8 p-6 bg-yellow-900 border border-yellow-600 rounded-lg">
          <div className="flex items-center space-x-3">
            <svg className="w-6 h-6 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div>
              <h3 className="text-lg font-medium text-yellow-200">No Sources Enabled</h3>
              <p className="text-yellow-100 mt-1">
                You have disabled all manga sources. Enable at least one source to search for manga.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Sources; 