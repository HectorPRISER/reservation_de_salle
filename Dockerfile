FROM node:22.14.0

WORKDIR /app

COPY package*.json ./

ENV NODE_ENV=development

RUN npm install --legacy-peer-deps --include=dev

COPY . .
RUN npm install -g nodemon

CMD ["npm", "run", "dev"]