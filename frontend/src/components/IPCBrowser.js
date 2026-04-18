import React, { useState, useEffect } from 'react';
import axios from 'axios';
import IPCMetadataPanel from './IPCMetadataPanel';
import { formatCitation, formatPunishment } from '../ipcUtils';
import { getApiBaseUrl } from '../config';

const IPCBrowser = () => {
  const [sections, setSections] = useState([]);
  const [filteredSections, setFilteredSections] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedChapter, setSelectedChapter] = useState('all');
  const [selectedSection, setSelectedSection] = useState(null);
  const [relatedSections, setRelatedSections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const apiUrl = getApiBaseUrl();

  // Fetch all IPC sections from the backend
  useEffect(() => {
    const fetchSections = async () => {
      try {
        setLoading(true);
        // IPC sections are public data, no authentication required
        const response = await axios.get(`${apiUrl}/ipc-sections`);
        
        const sections = response.data.sections;
        setSections(sections);
        setFilteredSections(sections);
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch IPC sections:', err);
        setError('Failed to load IPC sections. Please try again.');
        setLoading(false);
        
        // Fallback to sample data if API fails
        const sampleSections = [
          {
            section_number: "1",
            title: "Title and extent of operation of the Code",
            chapter: "Introduction",
            description: "This Act shall be called the Indian Penal Code, and shall take effect throughout India except the State of Jammu and Kashmir.",
            section_text: "This Act shall be called the Indian Penal Code, and shall take effect throughout India except the State of Jammu and Kashmir.",
            punishment: "N/A",
            citation: "Indian Penal Code, Section 1"
          },
          {
            section_number: "302",
            title: "Punishment for murder",
            chapter: "Of Offences affecting Life",
            description: "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
            section_text: "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be liable to fine.",
            punishment: "Death or imprisonment for life, and shall also be liable to fine",
            citation: "Indian Penal Code, Section 302"
          }
        ];
        
        setSections(sampleSections);
        setFilteredSections(sampleSections);
      }
    };
    
    fetchSections();
  }, [apiUrl]);

  useEffect(() => {
    let result = sections;
    
    if (searchTerm) {
      result = result.filter(section => 
        section.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        section.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        section.section_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (section.keywords && section.keywords.some(keyword => keyword.toLowerCase().includes(searchTerm.toLowerCase()))) ||
        (section.vector_search_terms && section.vector_search_terms.some(term => term.toLowerCase().includes(searchTerm.toLowerCase())))
      );
    }
    
    if (selectedChapter !== 'all') {
      result = result.filter(section => section.chapter?.chapter_name === selectedChapter);
    }
    
    setFilteredSections(result);
  }, [searchTerm, selectedChapter, sections]);

  const getChapters = () => {
    const chapters = sections.map(section => section.chapter?.chapter_name).filter(Boolean);
    return [...new Set(chapters)].sort();
  };

  const handleSectionClick = async (sectionNumber) => {
    try {
      const section = sections.find(s => s.section_number === sectionNumber);
      setSelectedSection(section);
      const relatedResponse = await axios.get(`${apiUrl}/ipc-section/${sectionNumber}/related`);
      setRelatedSections(relatedResponse.data.related_sections || []);
    } catch (err) {
      setError('Failed to load section details');
      console.error('Section load error:', err);
      setRelatedSections([]);
    }
  };

  const closeSectionDetail = () => {
    setSelectedSection(null);
    setRelatedSections([]);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
      <div className="py-2 sm:py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">IPC Section Browser</h1>
          <p className="mt-2 text-gray-600">
            Browse and search through IPC sections 1-511
          </p>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4 mb-6">
            <div className="text-sm text-red-700">
              {error}
            </div>
          </div>
        )}

        <div className="bg-white shadow rounded-lg">
          {/* Search and filter controls */}
          <div className="border-b border-gray-200 px-6 py-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-grow">
                <label htmlFor="search" className="sr-only">
                  Search IPC sections
                </label>
                <input
                  type="text"
                  name="search"
                  id="search"
                  placeholder="Search by title, description, or keywords..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                />
              </div>
              
              <div>
                <label htmlFor="chapter" className="sr-only">
                  Filter by chapter
                </label>
                <select
                  id="chapter"
                  value={selectedChapter}
                  onChange={(e) => setSelectedChapter(e.target.value)}
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                >
                  <option value="all">All Chapters</option>
                  {getChapters().map((chapter, index) => (
                    <option key={index} value={chapter}>{chapter}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Section list or detail view */}
          {selectedSection ? (
            /* Section Detail View */
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  Section {selectedSection.section_number}: {selectedSection.title}
                </h2>
                <button
                  onClick={closeSectionDetail}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Back to List
                </button>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Chapter</h3>
                    <p className="text-gray-700">{selectedSection.chapter?.chapter_name || 'General'}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Citation</h3>
                    <p className="text-gray-700">{formatCitation(selectedSection.citation)}</p>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Description</h3>
                  <p className="text-gray-700">{selectedSection.description}</p>
                </div>
                
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Section Text</h3>
                  <div className="bg-white p-4 rounded border border-gray-200">
                    <p className="text-gray-700 whitespace-pre-line">{selectedSection.section_text}</p>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Punishment</h3>
                  <p className="text-gray-700">{formatPunishment(selectedSection.punishment)}</p>
                </div>
                
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Dataset Metadata</h3>
                  <IPCMetadataPanel section={{ ...selectedSection, related_sections: relatedSections }} />
                </div>
              </div>
            </div>
          ) : (
            /* Section List View */
            <>
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-medium text-gray-900">
                    IPC Sections ({filteredSections.length} results)
                  </h2>
                  <p className="text-sm text-gray-500">
                    Showing sections 1-{Math.min(filteredSections.length, 100)} of {filteredSections.length}
                  </p>
                </div>
                
                {loading ? (
                  <div className="flex justify-center py-12">
                    <svg className="animate-spin h-10 w-10 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </div>
                ) : filteredSections.length === 0 ? (
                  <div className="text-center py-12">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h3 className="mt-2 text-lg font-medium text-gray-900">No sections found</h3>
                    <p className="mt-1 text-gray-500">
                      Try adjusting your search or filter criteria.
                    </p>
                  </div>
                ) : (
                  <ul className="divide-y divide-gray-200">
                    {filteredSections.slice(0, 100).map((section) => (
                      <li key={section.section_number} className="py-4">
                        <div 
                          className="block hover:bg-gray-50 cursor-pointer transition-colors duration-150"
                          onClick={() => handleSectionClick(section.section_number)}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="flex items-center">
                                <p className="text-lg font-medium text-primary-600">
                                  Section {section.section_number}
                                </p>
                                <span className="ml-4 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                  {section.chapter?.chapter_name || 'General'}
                                </span>
                                {section.severity_level && (
                                  <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-100 text-rose-800">
                                    {section.severity_level}
                                  </span>
                                )}
                              </div>
                              <p className="mt-1 text-base font-medium text-gray-900">
                                {section.title}
                              </p>
                              <p className="mt-1 text-sm text-gray-500">
                                {section.description}
                              </p>
                            </div>
                            <div className="ml-4 flex-shrink-0">
                              <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                              </svg>
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
              
              {/* Pagination */}
              {filteredSections.length > 100 && (
                <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                  <div className="flex-1 flex justify-between sm:hidden">
                    <button type="button" className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                      Previous
                    </button>
                    <button type="button" className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                      Next
                    </button>
                  </div>
                  <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-gray-700">
                        Showing <span className="font-medium">1</span> to <span className="font-medium">100</span> of{' '}
                        <span className="font-medium">{filteredSections.length}</span> results
                      </p>
                    </div>
                    <div>
                      <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                        <button type="button" className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
                          Previous
                        </button>
                        <button type="button" className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
                          Next
                        </button>
                      </nav>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
        
        <div className="mt-8 bg-blue-50 border-l-4 border-blue-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                <strong>Note:</strong> This browser contains IPC sections 1-511. All information is strictly grounded in the IPC dataset. 
                For comprehensive legal advice, please consult with a qualified legal professional.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IPCBrowser;
