import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import { config } from '../services/utils/config.js';

const __filename = fileURLToPath(import.meta.url);
const projectRoot = path.resolve(path.dirname(__filename), '../..');

export const runPythonAgent = (postcode) => {
  return new Promise((resolve, reject) => {
    const python = spawn('python', ['-m', 'backend.agent.start_agent', postcode], {
      env: { ...process.env, PYTHONPATH: projectRoot },
      shell: false,
    });

    let output = '';
    let error = '';
    let settled = false;

    const fail = (message) => {
      if (settled) return;
      settled = true;
      clearTimeout(timeout);
      reject(new Error(message));
    };

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.stderr.on('data', (data) => {
      error += data.toString();
    });

    const timeout = setTimeout(() => {
      python.kill('SIGKILL');
      console.error(`[python-agent] Timed out after ${config.PYTHON_TIMEOUT_MS}ms`);
      fail('Python process timed out');
    }, config.PYTHON_TIMEOUT_MS);

    python.on('error', (err) => {
      console.error('[python-agent] Failed to start:', err);
      fail('Unable to start Python agent');
    });

    python.on('close', (code) => {
      clearTimeout(timeout);

      if (settled) return;
      if (code !== 0) {
        settled = true;
        console.error(`[python-agent] Exited with code ${code}. stderr:\n${error.trim() || '(no stderr output)'}`);
        reject(new Error(`Python agent failed with exit code ${code}`));
      } else if (!output.trim()) {
        fail('Agent returned empty response');
      } else {
        settled = true;
        resolve(output.trim());
      }
    });
  });
};