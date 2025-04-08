FROM node:22.14.0

WORKDIR /app

RUN export JWT_SECRET=$(openssl rand -base64 32) && \
    echo "JWT_SECRET=$JWT_SECRET" >> .env

COPY package*.json ./

RUN npm install 

RUN npm install -g nodemon

COPY . .

CMD ["npm", "run", "dev"]
