FROM node:26-alpine AS builder

WORKDIR /app

COPY package.json  package-lock.json ./

RUN npm ci --omit=dev

COPY index.js ./

###part2###
FROM gcr.io/distroless/nodejs26-debian13:nonroot

WORKDIR /app

COPY --chown=nonroot:nonroot --from=builder /app/node_modules ./node_modules

COPY --chown=nonroot:nonroot --from=builder /app/index.js ./

EXPOSE 8080

CMD ["index.js"]

