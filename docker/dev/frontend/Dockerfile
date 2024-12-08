# Frontend Dockerfile (React)
FROM node:lts

# Set the working directory
WORKDIR /app

COPY docker/dev/frontend/devmode.sh /usr/local/bin/devmode.sh

EXPOSE 3000

CMD ["devmode.sh"]

# # Copy package.json and package-lock.json (if you have it)
# COPY frontend/package*.json ./

# # Install dependencies
# RUN npm install

# # Copy all other files
# COPY frontend/ ./

# # Expose port 3000
# EXPOSE 3000

# # Command to run the React app in development mode
# CMD ["npm", "start"]
