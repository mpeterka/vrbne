FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies only
RUN npm ci --omit=dev

# Copy pre-built application
COPY dist/ ./dist/
COPY templates/ ./templates/
COPY doc/ ./doc/

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
