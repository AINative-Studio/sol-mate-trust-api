FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM python:3.12-slim AS runner
WORKDIR /app
COPY --from=builder /app/out ./out
EXPOSE 3000
CMD ["sh", "-c", "python3 -m http.server ${PORT:-3000} --bind 0.0.0.0 --directory out"]
