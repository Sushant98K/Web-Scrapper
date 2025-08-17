# Google OAuth Setup Guide

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API and Google Identity API

## Step 2: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. Choose **Web application** as the application type
4. Add authorized origins:
   - `http://localhost:5173` (for development)
   - Your production domain (when deployed)
5. Add authorized redirect URIs:
   - `http://localhost:5173` (for development)
   - Your production domain (when deployed)

## Step 3: Configure Environment Variables

### Backend (.env)
\`\`\`env
GOOGLE_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
JWT_SECRET_KEY=your_very_long_and_secure_random_string_here
\`\`\`

### Frontend (.env)
\`\`\`env
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here.apps.googleusercontent.com
\`\`\`

## Step 4: Test Authentication

1. Start the backend server: `cd backend && python run.py`
2. Start the frontend server: `cd frontend && npm run dev`
3. Navigate to `http://localhost:5173`
4. Click "Sign in with Google" and test the authentication flow

## Security Notes

- Never commit your actual client secrets to version control
- Use different OAuth credentials for development and production
- Regularly rotate your JWT secret key
- Consider implementing refresh tokens for production use

## Troubleshooting

- **"Invalid client" error**: Check that your client ID matches exactly
- **"Redirect URI mismatch"**: Ensure your redirect URIs are configured correctly in Google Cloud Console
- **CORS errors**: Verify that your origins are properly configured
