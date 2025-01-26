# Указываем базовый образ
FROM node:22-alpine AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем весь проект в контейнер
COPY . .

# Сборка Next.js приложения
RUN npm run build

# Указываем легковесный образ для запуска приложения
FROM node:22-alpine AS runner

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем собранное приложение из предыдущего этапа
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package*.json ./

# Устанавливаем production-зависимости
RUN npm install --only=production

# Указываем порт, который использует приложение
EXPOSE 3000

# Команда запуска
CMD ["npm", "run", "start"]
