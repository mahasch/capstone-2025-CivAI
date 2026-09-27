export const config = {
  PORT: process.env.PORT || 3000,
  NODE_ENV: process.env.NODE_ENV || 'development',
  PYTHON_TIMEOUT_MS: parseInt(process.env.PYTHON_TIMEOUT_MS) || 20000,
  RATE_LIMIT_MAX: parseInt(process.env.RATE_LIMIT_MAX) || 30,
  CORS_ORIGIN: process.env.CORS_ORIGIN || 'http://localhost:4200',
};