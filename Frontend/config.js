window.APP_CONFIG = {
  apiBaseUrl: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:5000'
    : 'https://YOUR-RENDER-SERVICE.onrender.com'
};
