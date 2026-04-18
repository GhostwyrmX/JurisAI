import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import AIResponseDetails from './AIResponseDetails';
import { getApiBaseUrl } from '../config';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState('english');
  const [profession, setProfession] = useState('general');
  const [enableVoice, setEnableVoice] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState('');
  const [streamStatus, setStreamStatus] = useState('');
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const { currentUser } = useAuth();
  const demoQueries = [
    'A man threatened a shopkeeper with a knife and took cash from the counter.',
    'My phone was stolen on a bus and I want to file a complaint draft.',
    'Explain Section 420 IPC for a journalism student in simple terms.',
    'A group entered my house at night and damaged the door before stealing jewellery.',
  ];

  const apiUrl = getApiBaseUrl();

  const getSpeechLocale = (selectedLanguage) => {
    const localeMap = {
      english: 'en-IN',
      hindi: 'hi-IN',
      marathi: 'mr-IN',
      tamil: 'ta-IN',
      bengali: 'bn-IN'
    };

    return localeMap[selectedLanguage] || 'en-IN';
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechSupported(false);
      return undefined;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = getSpeechLocale(language);

    recognition.onstart = () => {
      setError('');
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0]?.transcript || '')
        .join(' ')
        .trim();

      setInput(transcript);
    };

    recognition.onerror = (event) => {
      setIsListening(false);
      if (event.error !== 'no-speech' && event.error !== 'aborted') {
        setError('Speech recognition failed. Please try again or type your query.');
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    setSpeechSupported(true);

    return () => {
      recognition.onstart = null;
      recognition.onresult = null;
      recognition.onerror = null;
      recognition.onend = null;
      recognition.stop();
      recognitionRef.current = null;
    };
  }, [language]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) {
      setError('Please enter a query');
      return;
    }

    if (input.length > 1000) {
      setError('Query is too long. Please limit to 1000 characters.');
      return;
    }

    try {
      setError('');
      
      // Add user message to chat
      const userMessage = {
        id: Date.now(),
        text: input,
        sender: 'user',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, userMessage]);
      setInput('');
      setLoading(true);

      const aiMessageId = Date.now() + 1;
      setMessages(prev => [...prev, {
        id: aiMessageId,
        text: '',
        sender: 'ai',
        timestamp: new Date(),
        isStreaming: true
      }]);

      // Send query to backend using streaming
      const token = localStorage.getItem('token');
      const response = await fetch(`${apiUrl}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          query: input,
          language,
          profession,
          enableVoice
        })
      });

      if (!response.ok || !response.body) {
        throw new Error(`Streaming failed with status ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        lines
          .map(line => line.trim())
          .filter(Boolean)
          .forEach((line) => {
            let parsed;
            try {
              parsed = JSON.parse(line);
            } catch (parseError) {
              return;
            }
            if (parsed.type === 'status') {
              setStreamStatus(parsed.message);
              return;
            }

            if (parsed.type === 'final') {
              const finalData = parsed.data;
              setMessages(prev => prev.map(message => (
                message.id === aiMessageId
                  ? {
                      ...message,
                      text: finalData.complete_response || finalData.analysis,
                      charges: finalData.charges,
                      matchedSections: finalData.matched_sections || [],
                      structuredResponse: finalData,
                      audioText: finalData.audio_text,
                      isStreaming: false
                    }
                  : message
              )));
              setStreamStatus('');
              return;
            }

            if (parsed.data) {
              setMessages(prev => prev.map(message => (
                message.id === aiMessageId
                  ? {
                      ...message,
                      text: `${message.text}${message.text ? '\n\n' : ''}${JSON.stringify(parsed.data, null, 2)}`,
                    }
                  : message
              )));
            }
          });
      }
    } catch (err) {
      console.error('Chat error:', err);
      
      let errorMessageText = 'Sorry, I encountered an error processing your request. Please try again.';
      
      // Provide more specific error messages
      if (err.response?.status === 500) {
        errorMessageText = 'Backend service is unavailable. Please check if the backend server is running.';
      } else if (err.code === 'NETWORK_ERROR' || err.message?.includes('Network Error')) {
        errorMessageText = 'Cannot connect to the backend service. Please check your internet connection and ensure the backend is deployed.';
      }
      
      setError(errorMessageText);
      
      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 2,
        text: errorMessageText,
        sender: 'ai',
        isError: true,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setStreamStatus('');
      setLoading(false);
    }
  };

  const handleScenarioExample = (scenario) => {
    setInput(scenario);
  };

  const toggleSpeechRecognition = () => {
    if (!speechSupported || !recognitionRef.current || loading) {
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      return;
    }

    recognitionRef.current.lang = getSpeechLocale(language);
    recognitionRef.current.start();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 sm:py-6 lg:px-8">
      <div className="py-2 sm:py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">AI Legal Assistant</h1>
          <p className="mt-2 text-gray-600">
            Ask legal questions or describe crime scenarios to get IPC-based analysis
          </p>
        </div>

        <div className="bg-white shadow rounded-lg">
          {/* Chat header with settings */}
          <div className="border-b border-gray-200 px-6 py-4">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:flex xl:flex-wrap xl:items-end">
                <div className="min-w-0">
                  <label htmlFor="language" className="block text-sm font-medium text-gray-700">
                    Language
                  </label>
                  <select
                    id="language"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                  >
                    <option value="english">English</option>
                    <option value="hindi">Hindi</option>
                    <option value="marathi">Marathi</option>
                    <option value="tamil">Tamil</option>
                    <option value="bengali">Bengali</option>
                  </select>
                </div>
                
                <div className="min-w-0">
                  <label htmlFor="profession" className="block text-sm font-medium text-gray-700">
                    Profession
                  </label>
                  <select
                    id="profession"
                    value={profession}
                    onChange={(e) => setProfession(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md"
                  >
                    <option value="general">General User</option>
                    <option value="lawyer">Lawyer</option>
                    <option value="police">Police Officer</option>
                    <option value="student">Law Student</option>
                    <option value="journalist">Journalist</option>
                  </select>
                </div>
                
                <div className="flex items-center self-start pt-1 sm:self-end">
                  <input
                    id="voice-toggle"
                    type="checkbox"
                    checked={enableVoice}
                    onChange={(e) => setEnableVoice(e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor="voice-toggle" className="ml-2 block text-sm text-gray-700">
                    Enable Voice Output
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Chat messages container */}
          <div className="chat-container overflow-y-auto p-3 sm:p-6">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-12">
                <div className="bg-primary-100 p-4 rounded-full mb-4">
                  <svg className="h-12 w-12 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">How can I help you today?</h3>
                <p className="text-gray-500 max-w-md">
                  Ask a legal question about the Indian Penal Code or describe a crime scenario for analysis.
                </p>
                
                <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {demoQueries.map((scenario) => (
                    <button
                      key={scenario}
                      onClick={() => handleScenarioExample(scenario)}
                      className="text-left p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <h4 className="font-medium text-gray-900">Demo Mode</h4>
                      <p className="mt-1 text-sm text-gray-500">{scenario}</p>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`message-bubble ${
                        message.sender === 'user'
                          ? 'user-message'
                          : message.isError
                          ? 'bg-red-100 text-red-800'
                          : 'bg-white text-gray-800 border border-gray-200 shadow-sm'
                      }`}
                    >
                      <div className="font-medium text-xs mb-1">
                        {message.sender === 'user' ? 'You' : 'JURIS AI'}
                      </div>
                      {message.sender === 'ai' && !message.isError ? (
                        <AIResponseDetails
                          responseText={message.text}
                          charges={message.charges}
                          matchedSections={message.matchedSections}
                          structuredResponse={message.structuredResponse}
                          language={language}
                        />
                      ) : (
                        <div className="whitespace-pre-wrap">{message.text}</div>
                      )}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="message-bubble ai-message">
                      <div className="space-y-2">
                        <div className="flex space-x-2">
                          <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
                          <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                        {streamStatus && <div className="text-xs text-gray-500">{streamStatus}</div>}
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Chat input form */}
          <div className="border-t border-gray-200 px-6 py-4">
            {error && (
              <div className="mb-4 rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-700">
                  {error}
                </div>
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row sm:space-x-4 sm:gap-0">
              <div className="flex-grow">
                <label htmlFor="chat-input" className="sr-only">Type your message</label>
                <textarea
                  id="chat-input"
                  rows={3}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask a legal question or describe a crime scenario..."
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  disabled={loading}
                />
                <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                  <span>
                    {speechSupported
                      ? isListening
                        ? 'Listening... speak now.'
                        : 'Use the mic to speak your query.'
                      : 'Speech-to-text is not supported in this browser.'}
                  </span>
                  {speechSupported && (
                    <button
                      type="button"
                      onClick={toggleSpeechRecognition}
                      disabled={loading}
                      className={`inline-flex items-center rounded-md px-3 py-1.5 font-medium transition-colors ${
                        isListening
                          ? 'bg-red-100 text-red-700 hover:bg-red-200'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      <svg className="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3zm5 11a5 5 0 01-10 0M5 19h14M12 19v4" />
                      </svg>
                      {isListening ? 'Stop Mic' : 'Speak'}
                    </button>
                  )}
                </div>
              </div>
              <div className="flex items-end sm:self-auto">
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="inline-flex w-full items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 sm:w-auto"
                >
                  {loading ? (
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    <svg className="-ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  )}
                  Send
                </button>
              </div>
            </form>
            
            <div className="mt-2 text-xs text-gray-500">
              {currentUser?.profession === 'lawyer' && (
                <p>Tip: As a lawyer, you can ask detailed questions about legal precedents and case applications.</p>
              )}
              {currentUser?.profession === 'police' && (
                <p>Tip: As a police officer, you can describe incidents for charge recommendations.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
