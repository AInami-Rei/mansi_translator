FROM node:12 AS build

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install -g npm@7 && npm install

COPY . .

RUN npm run build

FROM nginx:alpine AS run_prod

COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
