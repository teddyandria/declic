# Image du front Déclic : build Vite, puis fichiers statiques servis par Caddy.
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Le front appelle /api/… ; Caddy relaie vers l'API (même origine, pas de CORS).
ENV VITE_API_URL=/api
RUN npm run build

FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
