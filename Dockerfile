FROM node:22-alpine AS web-build
WORKDIR /build
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DOCURULE_DATA_DIR=/app/data
WORKDIR /app
COPY apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/api/src/ ./src/
COPY --from=web-build /build/dist ./static
RUN useradd --create-home --uid 10001 docurule && mkdir -p /app/data && chown -R docurule:docurule /app
USER docurule
EXPOSE 8080
CMD ["uvicorn", "docurule.main:app", "--app-dir", "/app/src", "--host", "0.0.0.0", "--port", "8080"]
