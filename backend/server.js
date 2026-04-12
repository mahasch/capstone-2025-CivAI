import express from 'express';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import morgan from 'morgan';
import dotenv from 'dotenv';

dotenv.config();

const app = express();

// Security & logging middleware
app.use(helmet());
app.use(express.json({ limit: '10kb' }));
app.use(morgan('combined'));

// Rate limiting to protect against abuse
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 30, // max 30 requests per minute
});
app.use(limiter);

// Fix __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Project root (adjust if backend is nested)
const projectRoot = path.resolve(__dirname, '..');

// Helper: spawn Python process as Promise
const runPythonAgent = (postcode) => {
  return new Promise((resolve, reject) => {
    const python = spawn(
      'python',
      ['-m', 'backend.start_agent', postcode],
      {
        env: { ...process.env, PYTHONPATH: projectRoot },
        shell: true,
      }
    );

    let output = '';
    let error = '';

    python.stdout.on('data', (data) => (output += data.toString()));
    python.stderr.on('data', (data) => (error += data.toString()));

    // Timeout after 20 seconds
    const timeout = setTimeout(() => {
      python.kill('SIGKILL');
      reject(new Error('Python process timed out'));
    }, 20000);

    python.on('close', (code) => {
      clearTimeout(timeout);
      if (code !== 0) {
        reject(new Error(error || `Python process exited with code ${code}`));
      } else {
        resolve(output.trim());
      }
    });
  });
};

// Endpoint
app.post('/postcode', async (req, res) => {
  const { postcode } = req.body;

  if (!postcode || typeof postcode !== 'string') {
    return res.status(400).json({ error: 'Invalid postcode' });
  }

  try {
    const markdown = await runPythonAgent(postcode);
    res.json({ markdown });
  } catch (err) {
    console.error('Python agent error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
