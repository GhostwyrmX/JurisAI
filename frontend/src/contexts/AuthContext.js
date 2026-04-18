import React, { useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { getApiBaseUrl } from '../config';

const AuthContext = React.createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const apiUrl = getApiBaseUrl();

  async function signup(username, email, password, profession, preferredLanguage) {
    const response = await axios.post(`${apiUrl}/signup`, {
      username,
      email,
      password,
      profession,
      preferredLanguage
    });
    
    localStorage.setItem('token', response.data.token);
    setCurrentUser(response.data.user);
    return response.data;
  }

  async function login(email, password) {
    const response = await axios.post(`${apiUrl}/login`, {
      email,
      password
    });
    
    localStorage.setItem('token', response.data.token);
    setCurrentUser(response.data.user);
    return response.data;
  }

  async function logout() {
    localStorage.removeItem('token');
    setCurrentUser(null);
  }

  async function updateUserProfile(profession, preferredLanguage) {
    const token = localStorage.getItem('token');
    const response = await axios.put(`${apiUrl}/user-profile`, {
      profession,
      preferredLanguage
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    
    setCurrentUser(response.data);
    return response.data;
  }

  const getUserProfile = useCallback(async () => {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${apiUrl}/user-profile`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    
    setCurrentUser(response.data);
    return response.data;
  }, [apiUrl]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and get user info
      getUserProfile()
        .catch(() => {
          // If token is invalid, remove it
          localStorage.removeItem('token');
          setCurrentUser(null);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [getUserProfile]);

  const value = {
    currentUser,
    loading,
    signup,
    login,
    logout,
    updateUserProfile,
    getUserProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
