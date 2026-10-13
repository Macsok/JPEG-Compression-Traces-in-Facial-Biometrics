FROM node:22-alpine
WORKDIR /check
RUN npm install --ignore-scripts --no-audit --no-fund jsdom@26.1.0
COPY app/static/ app/static/
COPY app/templates/index.html app/templates/index.html
COPY tests/localization.cjs tests/localization.cjs
RUN node tests/localization.cjs
