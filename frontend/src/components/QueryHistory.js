import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import AIResponseDetails from './AIResponseDetails';
import { getApiBaseUrl } from '../config';

const QueryHistory = () => {
  const [queries, setQueries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [selectedQuery, setSelectedQuery] = useState(null);
  const [generatingAudio, setGeneratingAudio] = useState(false);

  const apiUrl = getApiBaseUrl();
  const ITEMS_PER_PAGE = 10;

  const loadQueries = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await axios.get(`${apiUrl}/history?limit=${ITEMS_PER_PAGE}&skip=${page * ITEMS_PER_PAGE}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (page === 0) {
        setQueries(response.data);
      } else {
        setQueries(prev => [...prev, ...response.data]);
      }
      
      setHasMore(response.data.length === ITEMS_PER_PAGE);
      setError('');
    } catch (err) {
      setError('Failed to load query history');
      console.error('History load error:', err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, page]);

  useEffect(() => {
    loadQueries();
  }, [loadQueries]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const loadMore = () => {
    setPage(prev => prev + 1);
  };

  const playAudio = (audioData) => {
    if (audioData) {
      const audio = new Audio(audioData);
      audio.play().catch(err => {
        console.error('Error playing audio:', err);
        setError('Failed to play audio response.');
      });
    }
  };

  const clearHistory = async () => {
    if (window.confirm('Are you sure you want to clear your query history? This cannot be undone.')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${apiUrl}/history`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        setQueries([]);
        setError('');
      } catch (err) {
        setError('Failed to clear history');
        console.error('Clear history error:', err);
      }
    }
  };

  const handleQueryClick = (query) => {
    setSelectedQuery(query);
  };

  const closeQueryDetail = () => {
    setSelectedQuery(null);
  };

  const generateAudioForQuery = async (query) => {
    try {
      setGeneratingAudio(true);
      
      // Generate audio for the stored response text
      const token = localStorage.getItem('token');
      const response = await axios.post(`${apiUrl}/generate-audio`, {
        text: query.response,
        language: query.language || 'english'
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      // Update the query in the list with new audio data
      setQueries(prev => prev.map(q => 
        q._id === query._id 
          ? { ...q, audioData: response.data.audio_path }
          : q
      ));

      // Update selected query if it's the current one
      if (selectedQuery && selectedQuery._id === query._id) {
        setSelectedQuery(prev => ({ ...prev, audioData: response.data.audio_path }));
      }

      setError('');
    } catch (err) {
      setError('Failed to generate audio');
      console.error('Audio generation error:', err);
    } finally {
      setGeneratingAudio(false);
    }
  };

  const deleteQuery = async (queryId) => {
    if (window.confirm('Are you sure you want to delete this query? This cannot be undone.')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${apiUrl}/query/${queryId}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        // Remove the query from the list
        setQueries(prev => prev.filter(q => q._id !== queryId));
        
        // Close detail view if this query was selected
        if (selectedQuery && selectedQuery._id === queryId) {
          setSelectedQuery(null);
        }
        
        setError('');
      } catch (err) {
        setError('Failed to delete query');
        console.error('Delete query error:', err);
      }
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
      <div className="py-2 sm:py-6">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Query History</h1>
            <p className="mt-2 text-gray-600">
              Your previous legal queries and AI responses
            </p>
          </div>
          {queries.length > 0 && (
            <button
              onClick={clearHistory}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <svg className="-ml-1 mr-2 h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Clear History
            </button>
          )}
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4 mb-6">
            <div className="text-sm text-red-700">
              {error}
            </div>
          </div>
        )}

        {loading && queries.length === 0 ? (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <div className="px-4 py-5 sm:px-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            </div>
          </div>
        ) : queries.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <h3 className="mt-2 text-lg font-medium text-gray-900">No query history</h3>
            <p className="mt-1 text-gray-500">
              Get started by asking a legal question in the{' '}
              <a href="/chat" className="text-primary-600 hover:text-primary-500">
                AI Assistant
              </a>.
            </p>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {queries.map((query) => (
                <li key={query._id}>
                  <div className="px-4 py-5 sm:px-6 hover:bg-gray-50 cursor-pointer" onClick={() => handleQueryClick(query)}>
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-gray-500">
                        {formatDate(query.timestamp)}
                      </p>
                      <div className="flex items-center space-x-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          IPC Query
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteQuery(query._id);
                          }}
                          className="text-red-600 hover:text-red-800 p-1"
                          title="Delete this query"
                        >
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    <div className="mt-2">
                      <p className="text-lg font-medium text-gray-900">Q: {query.query}</p>
                      <div className="mt-2 text-gray-700">
                        <p className="font-medium">A:</p>
                        <div className="line-clamp-3 whitespace-pre-wrap">{query.response}</div>
                      </div>
                      {query.audioData && (
                        <div className="mt-2">
                          <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-100 text-green-800">
                            <svg className="mr-1 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                            </svg>
                            Audio Available
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
            
            {hasMore && (
              <div className="bg-white px-4 py-3 flex items-center justify-center border-t border-gray-200 sm:px-6">
                <button
                  onClick={loadMore}
                  disabled={loading}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Loading...
                    </>
                  ) : (
                    'Load More'
                  )}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Query Detail Modal */}
      {selectedQuery && (
        <div className="fixed inset-0 z-50 h-full w-full overflow-y-auto bg-gray-600 bg-opacity-50 p-2 sm:p-4" onClick={closeQueryDetail}>
          <div className="relative mx-auto my-4 max-h-[95vh] w-full max-w-4xl overflow-y-auto rounded-md border bg-white p-4 shadow-lg sm:my-10 sm:p-5" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Query Details</h3>
              <button
                onClick={closeQueryDetail}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500 mb-1">Date: {formatDate(selectedQuery.timestamp)}</p>
                <p className="text-sm text-gray-500 mb-4">
                  Language: {selectedQuery.language || 'English'} | Profession: {selectedQuery.profession || 'General'}
                </p>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Question:</h4>
                <p className="text-gray-700">{selectedQuery.query}</p>
              </div>

              <AIResponseDetails
                responseText={selectedQuery.response}
                charges={selectedQuery.charges}
                matchedSections={selectedQuery.matchedSections}
                structuredResponse={selectedQuery.responsePayload}
                language={selectedQuery.language}
              />

              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-3">
                  {selectedQuery.audioData ? (
                    <button
                      onClick={() => playAudio(selectedQuery.audioData)}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                    >
                      <svg className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                      </svg>
                      Play Audio Response
                    </button>
                  ) : (
                    <button
                      onClick={() => generateAudioForQuery(selectedQuery)}
                      disabled={generatingAudio}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
                    >
                      {generatingAudio ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Generating Audio...
                        </>
                      ) : (
                        <>
                          <svg className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                          </svg>
                          Generate Audio
                        </>
                      )}
                    </button>
                  )}
                </div>

                <button
                  onClick={() => deleteQuery(selectedQuery._id)}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <svg className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Delete Query
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryHistory;
