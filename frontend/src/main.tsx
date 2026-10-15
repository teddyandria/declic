import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router'

import './index.css'
import { AddLesson } from './pages/AddLesson'
import { Home } from './pages/Home'
import { Lesson } from './pages/Lesson'

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1 } },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/ajouter" element={<AddLesson />} />
          <Route path="/lecons/:id" element={<Lesson />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
