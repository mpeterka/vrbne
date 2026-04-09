FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install all dependencies (including dev for build)
RUN npm ci

# Copy source code
COPY src/ ./src/
COPY templates/ ./templates/
COPY doc/ ./doc/

# Build TypeScript (nebo může být prebuildované z CI/CD)
RUN npm run build || echo "dist/ already exists from CI/CD"

# Remove dev dependencies
RUN npm prune --omit=dev

# Install curl for healthcheck
RUN apk add --no-cache curl

# Create non-root user before changing ownership
RUN addgroup -g 1001 -S vrbneuser && adduser -S vrbneuser -u 1001

# Fix ownership for all files so vrbneuser can read them
RUN chown -R vrbneuser:vrbneuser /app

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Use non-root user for security
USER vrbneuser

# Expose port
EXPOSE 8000

# Start application
CMD ["npm", "start"]
