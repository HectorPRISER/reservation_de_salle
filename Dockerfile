FROM node:22.14.0

WORKDIR /app

# Generate a JWT secret and set it as an environment variable
RUN export JWT_SECRET=$(openssl rand -base64 32) && \
    echo "JWT_SECRET=$JWT_SECRET" >> .env

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies (including dev dependencies)
RUN npm install 

# Install nodemon globally
RUN npm install -g nodemon

# Copy all other files to the container
COPY . .

# Start the application
CMD ["npm", "run", "dev"]
