# 1) Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Accept build argument from docker-compose
ARG API_BASE_URL
# Export as env so we can reuse it
ENV VITE_API_BASE_URL=${API_BASE_URL}

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Generate a .env.production file inside the build container
# so Vite can read VITE_API_BASE_URL from it
RUN echo "VITE_API_BASE_URL=${VITE_API_BASE_URL}" > .env.production

# Now run Vite build in production mode
RUN npm run build

# 2) Runtime stage with Nginx
FROM nginx:stable-alpine

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy build output from Vite
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
