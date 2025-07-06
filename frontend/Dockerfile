# 1) Build
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 2) Serve
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# History API fallback
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/
EXPOSE 5173 80
CMD ["nginx","-g","daemon off;"]
