import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const UserProfile = () => {
  const [profession, setProfession] = useState('general');
  const [preferredLanguage, setPreferredLanguage] = useState('english');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const { currentUser, getUserProfile, updateUserProfile } = useAuth();

  useEffect(() => {
    if (currentUser) {
      setProfession(currentUser.profession || 'general');
      setPreferredLanguage(currentUser.preferredLanguage || 'english');
    }
  }, [currentUser]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      await updateUserProfile(profession, preferredLanguage);
      setSuccess('Profile updated successfully!');
      
      // Refresh user data
      await getUserProfile();
    } catch (err) {
      setError('Failed to update profile. Please try again.');
      console.error('Profile update error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="md:grid md:grid-cols-3 md:gap-6">
          <div className="md:col-span-1">
            <h1 className="text-3xl font-bold text-gray-900">Your Profile</h1>
            <p className="mt-2 text-gray-600">
              Manage your account settings and preferences
            </p>
          </div>
          
          <div className="mt-5 md:mt-0 md:col-span-2">
            <form onSubmit={handleSubmit}>
              <div className="shadow sm:rounded-md sm:overflow-hidden">
                <div className="px-4 py-5 bg-white sm:p-6">
                  <div className="grid grid-cols-6 gap-6">
                    <div className="col-span-6">
                      <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                        Username
                      </label>
                      <input
                        type="text"
                        name="username"
                        id="username"
                        value={currentUser?.username || ''}
                        disabled
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-gray-50"
                      />
                    </div>
                    
                    <div className="col-span-6">
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                        Email Address
                      </label>
                      <input
                        type="email"
                        name="email"
                        id="email"
                        value={currentUser?.email || ''}
                        disabled
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm bg-gray-50"
                      />
                    </div>
                    
                    <div className="col-span-6 sm:col-span-3">
                      <label htmlFor="profession" className="block text-sm font-medium text-gray-700">
                        Profession
                      </label>
                      <select
                        id="profession"
                        name="profession"
                        value={profession}
                        onChange={(e) => setProfession(e.target.value)}
                        className="mt-1 block w-full bg-white border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      >
                        <option value="general">General User</option>
                        <option value="lawyer">Lawyer</option>
                        <option value="police">Police Officer</option>
                        <option value="student">Law Student</option>
                        <option value="journalist">Journalist</option>
                      </select>
                      <p className="mt-1 text-sm text-gray-500">
                        Your profession helps us tailor responses to your needs
                      </p>
                    </div>
                    
                    <div className="col-span-6 sm:col-span-3">
                      <label htmlFor="language" className="block text-sm font-medium text-gray-700">
                        Preferred Language
                      </label>
                      <select
                        id="language"
                        name="language"
                        value={preferredLanguage}
                        onChange={(e) => setPreferredLanguage(e.target.value)}
                        className="mt-1 block w-full bg-white border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      >
                        <option value="english">English</option>
                        <option value="hindi">Hindi</option>
                        <option value="marathi">Marathi</option>
                        <option value="tamil">Tamil</option>
                        <option value="bengali">Bengali</option>
                      </select>
                      <p className="mt-1 text-sm text-gray-500">
                        Default language for AI responses
                      </p>
                    </div>
                    
                    <div className="col-span-6">
                      <label className="block text-sm font-medium text-gray-700">
                        Account Created
                      </label>
                      <p className="mt-1 text-sm text-gray-900">
                        {currentUser?.createdAt ? new Date(currentUser.createdAt).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        }) : 'Unknown'}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
                  {error && (
                    <div className="mb-4 rounded-md bg-red-50 p-4">
                      <div className="text-sm text-red-700">
                        {error}
                      </div>
                    </div>
                  )}
                  
                  {success && (
                    <div className="mb-4 rounded-md bg-green-50 p-4">
                      <div className="text-sm text-green-700">
                        {success}
                      </div>
                    </div>
                  )}
                  
                  <button
                    type="submit"
                    disabled={loading}
                    className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Saving...
                      </>
                    ) : (
                      'Save Changes'
                    )}
                  </button>
                </div>
              </div>
            </form>
            
            <div className="mt-10 sm:mt-0">
              <div className="md:grid md:grid-cols-3 md:gap-6">
                <div className="md:col-span-1">
                  <h3 className="text-lg font-medium text-gray-900">Privacy & Security</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Manage your privacy settings and security preferences
                  </p>
                </div>
                <div className="mt-5 md:mt-0 md:col-span-2">
                  <div className="shadow sm:rounded-md sm:overflow-hidden">
                    <div className="px-4 py-5 bg-white sm:p-6">
                      <div className="grid grid-cols-6 gap-6">
                        <div className="col-span-6">
                          <div className="flex items-start">
                            <div className="flex items-center h-5">
                              <input
                                id="privacy"
                                name="privacy"
                                type="checkbox"
                                className="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300 rounded"
                              />
                            </div>
                            <div className="ml-3 text-sm">
                              <label htmlFor="privacy" className="font-medium text-gray-700">
                                Share anonymized query data for research
                              </label>
                              <p className="text-gray-500">
                                Help improve our legal AI by allowing us to use anonymized query data for research purposes.
                              </p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="col-span-6">
                          <div>
                            <h4 className="text-md font-medium text-gray-900">Change Password</h4>
                            <p className="mt-1 text-sm text-gray-500">
                              For security reasons, password changes must be done through our secure portal.
                            </p>
                            <button
                              type="button"
                              className="mt-2 inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                            >
                              Change Password
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;