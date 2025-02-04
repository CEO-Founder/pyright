 "App.tsx
import React from 'react';
import { Helmet } from 'react-helmet';

const App: React.FC = () => {
  return (
    <div>
      <Helmet>
        {/* Security headers */}
        <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'" />
        <meta http-equiv="X-Content-Type-Options" content="nosniff" />
        <meta http-equiv="X-Frame-Options" content="DENY" />
      </Helmet>
      
      <h1>Welcome to My Secure Portfolio</h1>
      <ContactForm />
    </div>
  );
};

// Secure form component with input validation
const ContactForm: React.FC = () => {
  const [message, setMessage] = React.useState('');

  const sanitizeInput = (input: string) => {
    return input.replace(/<[^>]*>?/gm, ''); // Sanitize HTML tags
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const sanitizedMessage = sanitizeInput(message);
    // Send to backend API
  };

  return (
    <form onSubmit={handleSubmit}>
      <textarea 
        value={message} 
        onChange={(e) => setMessage(e.target.value)} 
        placeholder="Your message..."
      />
      <button type="submit">Send</button>
    </form>
  );
};
// server.ts
import express from 'express';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import cors from 'cors';
import { body, validationResult } from 'express-validator';

const app = express();
const port = 3000;

// Security middleware
app.use(helmet()); // Sets secure headers
app.use(cors({ origin: 'https://yourdomain.com' })); // Restrict CORS
app.use(express.json()); // Parse JSON safely

// Rate limiting (100 requests per 15 minutes)
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
});
app.use(limiter);

// Example secure API endpoint
app.post(
  '/api/contact',
  [
    body('message').trim().escape(), // Sanitize input
  ],
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Process sanitized message
    console.log(req.body.message);
    res.status(200).send('Message received!');
  }
);

// HTTPS enforcement (use in production)
if (process.env.NODE_ENV === 'production') {
  app.use((req, res, next) => {
    if (req.headers['x-forwarded-proto'] !== 'https') {
      res.redirect(301, `https://${req.headers.host}${req.url}`);
    } else {
      next();
    }
  });
}

app.listen(port, () => {
  console.log(`Server running at https://localhost:${port}`);
});
<!-- Public/index.html -->
<meta http-equiv="Content-Security-Policy" 
  content="default-src 'self'; 
  script-src 'self' 'unsafe-inline'; 
  style-src 'self' 'unsafe-inline'; 
  img-src 'self' data:; 
  connect-src 'self' https://api.yourdomain.com">
  // Example with pg library
import { Pool } from 'pg';
const pool = new Pool({ ssl: { rejectUnauthorized: true } });

const getUser = async (userId: string) => {
  const result = await pool.query
    'SELECT * FROM users WHERE id = $1', 
    [userId] // Parameterized query
  );
  return result.rows;
};
# .env
DB_URL=postgres://user:password@host:port/db?ssl=true
JWT_SECRET=your_secure_secret_here