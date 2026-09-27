import { Router } from 'express';
import { validatePostcode } from '../utils/validation.js';
import { runPythonAgent } from '../../agent/pythonAgent.js';

export const postcodeRouter = Router();

postcodeRouter.post('/postcode', async (req, res) => {
  try {
    const validation = validatePostcode(req.body.postcode);
    
    if (!validation.valid) {
      return res.status(400).json({ error: validation.error });
    }

    const markdown = await runPythonAgent(validation.postcode);
    res.json({ markdown });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`[${req.method} ${req.originalUrl}] Request failed:`, message);
    
    const statusCode = message.includes('timed out') ? 504 : 500;
    res.status(statusCode).json({ error: message });
  }
});