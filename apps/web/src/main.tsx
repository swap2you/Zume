import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import './styles.css'
import { Layout } from './components/Layout'
import { Ask } from './pages/Ask'
import { Home } from './pages/Home'
import { Builder, Finalize, Intake, Lab, Library, Practice, Settings } from './pages/WorkspacePages'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/intake" element={<Intake />} />
          <Route path="/finalize" element={<Finalize />} />
          <Route path="/library" element={<Library />} />
          <Route path="/practice" element={<Practice />} />
          <Route path="/builder" element={<Builder />} />
          <Route path="/lab" element={<Lab />} />
          <Route path="/ask" element={<Ask />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
