import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

// Design system styles (order matters: variables → fonts → global)
import './styles/variables.css'
import './styles/fonts.css'
import './styles/global.css'

import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
