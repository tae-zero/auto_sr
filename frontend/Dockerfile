# Build stage
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Set environment variables
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NODE_ENV=development

# Start the application in development mode with SWC disabled
CMD ["npm", "run", "dev", "--", "--turbo"] 