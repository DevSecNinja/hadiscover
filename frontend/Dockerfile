# Build stage
FROM node:24-alpine@sha256:931d7d57f8c1fd0e2179dbff7cc7da4c9dd100998bc2b32afc85142d8efbc213 AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the application with static export
# The build process will use NEXT_PUBLIC_API_URL from build args
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Allows to set the node environment
ARG NODE_ENV
ENV NODE_ENV=${NODE_ENV:-production}

# Remove basePath for Docker deployment (only needed for GitHub Pages)
RUN sed -i '/basePath:/d' next.config.ts

RUN npm run build

# Production stage with nginx to serve static files
FROM nginx:alpine@sha256:7d7a15b8a280c661051955f14c2b91fed3e23724ddba18d2f53e8b44e74ab37a AS runner

# Remove inherited maintainer label from base image
LABEL maintainer=""

WORKDIR /usr/share/nginx/html

# Remove default nginx static files
RUN rm -rf ./*

# Copy built static files from builder
COPY --from=builder /app/out .

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Set up proper permissions for nginx user
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Switch to non-root user
USER nginx

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -fsS http://127.0.0.1:80/health.html || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
