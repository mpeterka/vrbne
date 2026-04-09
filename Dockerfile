# Stage 1: Dependencies and Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./
COPY tsconfig.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm ci

# Copy source code and necessary folders for build
COPY src/ ./src/
COPY templates/ ./templates/

# Build TypeScript to dist/
RUN npm run build

# Stage 2: Final Runtime Image
FROM node:20-alpine AS runner

# Set production environment
ENV NODE_ENV=production

WORKDIR /app

# Add non-root user for security early to use in COPY
RUN addgroup -g 1001 -S vrbneuser && adduser -S vrbneuser -u 1001

# Install curl for healthcheck (minimal size in alpine)
RUN apk add --no-cache curl

# Copy only production package files
COPY package*.json ./

# Install ONLY production dependencies
RUN npm ci --omit=dev && npm cache clean --force

# Copy only built artifacts and necessary assets from builder stage
# Using --chown during COPY is more efficient than separate RUN chown
COPY --from=builder --chown=vrbneuser:vrbneuser /app/dist ./dist
COPY --from=builder --chown=vrbneuser:vrbneuser /app/templates ./templates
COPY --chown=vrbneuser:vrbneuser doc/ ./doc/
# Ensure package.json is also owned by the user if needed by npm start
RUN chown vrbneuser:vrbneuser package.json

# Use non-root user
USER vrbneuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Expose port
EXPOSE 8000

# Start application using the production build
CMD ["npm", "start"]
