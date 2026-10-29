import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { setupMockInterceptor } from './utils/mockInterceptor.js'

// Activate client-side mock backend interceptor (seamless fallback on GitHub Pages & offline)
setupMockInterceptor();

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
