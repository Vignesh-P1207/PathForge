FROM node:20-alpine AS build
WORKDIR /app

# Copy package files first — cache layer: npm install only reruns if package.json changes
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

# Copy source after deps are installed
COPY . .

# Use Docker-specific env (API calls go through nginx proxy at /api/)
RUN cp .env.docker .env && npm run build

# ── Production nginx stage ────────────────────────────────────────────────────
FROM nginx:1.27-alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy optimized nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
