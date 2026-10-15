import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router'

import './index.css'
import { RequireAuth } from './components/RequireAuth'
import { AddLesson } from './pages/AddLesson'
import { Data } from './pages/Data'
import { Home } from './pages/Home'
import { Lesson } from './pages/Lesson'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Session } from './pages/Session'
import { SessionEnd } from './pages/SessionEnd'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1 } },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/connexion" element={<Login />} />
          <Route path="/inscription" element={<Register />} />
          <Route path="/" element={<RequireAuth><Home /></RequireAuth>} />
          <Route path="/ajouter" element={<RequireAuth><AddLesson /></RequireAuth>} />
          <Route path="/lecons/:id" element={<RequireAuth><Lesson /></RequireAuth>} />
          <Route path="/seance" element={<RequireAuth><Session /></RequireAuth>} />
          <Route path="/fin" element={<RequireAuth><SessionEnd /></RequireAuth>} />
          <Route path="/donnees" element={<RequireAuth><Data /></RequireAuth>} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
