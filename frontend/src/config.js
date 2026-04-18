const trimTrailingSlash = (value) => value.replace(/\/+$/, '');

export const getApiBaseUrl = () => {
  const configuredUrl = process.env.REACT_APP_API_URL?.trim();
  if (configuredUrl) {
    return trimTrailingSlash(configuredUrl);
  }

  if (typeof window === 'undefined') {
    return 'http://localhost:3001';
  }

  const { hostname, origin } = window.location;
  const isLocalhost = ['localhost', '127.0.0.1'].includes(hostname);
  const isVercel = hostname.includes('.vercel.app');

  // For Vercel deployment without backend, show a helpful error
  if (isVercel && !configuredUrl) {
    console.error('Backend URL not configured. Please set REACT_APP_API_URL environment variable.');
    return origin; // This will fail, but we'll handle it in the UI
  }

  return isLocalhost ? 'http://localhost:3001' : (configuredUrl || trimTrailingSlash(origin));
};
