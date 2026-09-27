import cors from 'cors';
import helmet from 'helmet';
import express from 'express';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import { config } from '../utils/config.js';

export const setupMiddleware = (app) => {
  app.use(cors({ origin: config.CORS_ORIGIN, methods: ['POST', 'OPTIONS'] }));
  app.use(helmet());
  app.use(express.json({ limit: '10kb' }));
  app.use(morgan(config.NODE_ENV === 'production' ? 'combined' : 'dev'));
  app.use(
    rateLimit({
      windowMs: 60 * 1000,
      max: config.RATE_LIMIT_MAX,
      message: 'Too many requests',
    })
  );
};