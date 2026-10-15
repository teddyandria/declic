import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { setToken } from '../lib/token'
import { apiFetch, apiPostForm, apiUpload } from './client'
import type {
  CardData,
  CardUpdate,
  FinishResult,
  LessonDetail,
  LessonSummary,
  Me,
  ReviewResult,
  SessionCard,
  Token,
} from './types'

export function useMe() {
  return useQuery({ queryKey: ['me'], queryFn: () => apiFetch<Me>('/me') })
}

export function useLessons() {
  return useQuery({ queryKey: ['lessons'], queryFn: () => apiFetch<LessonSummary[]>('/lessons') })
}

export function useLesson(id: number) {
  return useQuery({ queryKey: ['lessons', id], queryFn: () => apiFetch<LessonDetail>(`/lessons/${id}`) })
}

/** Aperçu pour l'accueil : combien de cartes attendent. */
export function useSessionPreview() {
  return useQuery({ queryKey: ['session', 'preview'], queryFn: () => apiFetch<SessionCard[]>('/session') })
}

/** Cartes d'une séance : chargées une fois, jamais rafraîchies en cours de partie. */
export function useSessionCards(lessonId: number | null) {
  return useQuery({
    queryKey: ['session', 'play', lessonId],
    queryFn: () => apiFetch<SessionCard[]>(lessonId ? `/session?lesson_id=${lessonId}` : '/session'),
    staleTime: Infinity,
    gcTime: 0,
    refetchOnWindowFocus: false,
  })
}

export function useCreateLesson() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: { title: string; text: string }) =>
      apiFetch<LessonDetail>('/lessons', { method: 'POST', body: JSON.stringify(body) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lessons'] }),
  })
}

export function useGenerateCards() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (lessonId: number) => apiFetch<LessonDetail>(`/lessons/${lessonId}/generate`, { method: 'POST' }),
    onSuccess: (lesson) => {
      queryClient.setQueryData(['lessons', lesson.id], lesson)
      void queryClient.invalidateQueries({ queryKey: ['lessons'] })
      void queryClient.invalidateQueries({ queryKey: ['session'] })
    },
  })
}

export function useTranscribePhoto() {
  return useMutation({
    mutationFn: (photo: File) => {
      const form = new FormData()
      form.append('photo', photo)
      return apiUpload<{ text: string }>('/lessons/from-photo', form)
    },
  })
}

export function useDeleteLesson() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (lessonId: number) => apiFetch<void>(`/lessons/${lessonId}`, { method: 'DELETE' }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['lessons'] })
      void queryClient.invalidateQueries({ queryKey: ['session'] })
    },
  })
}

export function useUpdateCard(lessonId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...body }: CardUpdate & { id: number }) =>
      apiFetch<CardData>(`/cards/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lessons', lessonId] }),
  })
}

export function useDeleteCard() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (cardId: number) => apiFetch<void>(`/cards/${cardId}`, { method: 'DELETE' }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['lessons'] })
      void queryClient.invalidateQueries({ queryKey: ['session'] })
    },
  })
}

export function useReview() {
  return useMutation({
    mutationFn: (body: { card_id: number; answer: string }) =>
      apiFetch<ReviewResult>('/reviews', { method: 'POST', body: JSON.stringify(body) }),
  })
}

export function useFinishSession() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => apiFetch<FinishResult>('/session/finish', { method: 'POST' }),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ['me'] })
      void queryClient.invalidateQueries({ queryKey: ['session'] })
      void queryClient.invalidateQueries({ queryKey: ['lessons'] })
    },
  })
}

export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ pseudo, password }: { pseudo: string; password: string }) =>
      apiPostForm<Token>('/auth/login', { username: pseudo, password }),
    onSuccess: ({ access_token }) => {
      queryClient.clear() // pas de données d'un compte précédent
      setToken(access_token)
    },
  })
}

export function useRegister() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: { pseudo: string; password: string; consent: true }) =>
      apiFetch<Token>('/auth/register', { method: 'POST', body: JSON.stringify(body) }),
    onSuccess: ({ access_token }) => {
      queryClient.clear()
      setToken(access_token)
    },
  })
}

export function useDeleteAccount() {
  return useMutation({ mutationFn: () => apiFetch<void>('/me', { method: 'DELETE' }) })
}
