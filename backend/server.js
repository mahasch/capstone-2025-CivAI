import express from 'express';
import dotenv from 'dotenv';
import { config } from './services/utils/config.js'
import { postcodeRouter } from './services/routes/postcode.js';
import { setupMiddleware } from './services/middleware/index.js';
dotenv.config();

const app = express();

setupMiddleware(app);
app.use('/api', postcodeRouter);

app.listen(config.PORT, () => {
  console.log(`Server running on port ${config.PORT} (${config.NODE_ENV})`);
});