FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY src/ ./src/
COPY templates/ ./templates/
COPY doc/ ./doc/

# Build TypeScript
RUN npm run build

# Remove dev dependencies
RUN npm ci --only=production

# Install curl for healthcheck
RUN apk add --no-cache curl

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Use non-root user for security
RUN addgroup -g 1001 -S vrbneuser && adduser -S vrbneuser -u 1001
USER vrbneuser

# Expose port
EXPOSE 8000

# Start application
CMD ["npm", "start"]
