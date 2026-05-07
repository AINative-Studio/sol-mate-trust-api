FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
RUN npm install -g serve@14
COPY --from=builder /app/out ./out
EXPOSE 3000
CMD ["sh", "-c", "serve out -p ${PORT:-3000} --no-clipboard"]
