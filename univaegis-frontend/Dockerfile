# frontend/Dockerfile

# 1) Build stage
FROM node:18-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
# Use Vite build
RUN npm run build

# 2) Runtime stage with Nginx
FROM nginx:stable-alpine

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy build output from Vite
COPY --from=build /app/dist /usr/share/nginx/html

# Copy a basic nginx config (we'll keep default for now)
# You can later add a custom config if needed.
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
