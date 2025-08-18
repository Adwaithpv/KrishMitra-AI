# Vercel Deployment Guide for KrishMitraAI

This guide will help you deploy the KrishMitraAI FastAPI backend to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally with `npm i -g vercel`
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Environment Variables Setup

Before deploying, you'll need to set up environment variables in Vercel:

### Required Environment Variables

1. **GEMINI_API_KEY**: Your Google Gemini API key
   - Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Optional Environment Variables

- `LOCAL_MODEL`: Fallback local LLM (default: `microsoft/DialoGPT-small`)
- `EMBEDDING_MODEL`: Vector embedding model (default: `all-MiniLM-L6-v2`)
- `QDRANT_URL`: Vector database URL (if using external Qdrant)
- `REDIS_URL`: Cache database URL (if using external Redis)

## Deployment Steps

### Method 1: Using Vercel CLI (Recommended)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Navigate to your project directory**:
   ```bash
   cd agri-advisor
   ```

4. **Deploy to Vercel**:
   ```bash
   vercel
   ```

5. **Follow the prompts**:
   - Link to existing project or create new
   - Set project name (e.g., `krishmitra-ai-api`)
   - Confirm deployment settings

6. **Set environment variables**:
   ```bash
   vercel env add GEMINI_API_KEY
   # Enter your API key when prompted
   ```

7. **Redeploy with environment variables**:
   ```bash
   vercel --prod
   ```

### Method 2: Using Vercel Dashboard

1. **Push your code to GitHub/GitLab**

2. **Go to Vercel Dashboard**:
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"

3. **Import your repository**:
   - Select your Git provider
   - Choose the `agri-advisor` repository
   - Vercel will auto-detect it's a Python project

4. **Configure project settings**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (root of repository)
   - **Build Command**: Leave empty (Vercel will auto-detect)
   - **Output Directory**: Leave empty

5. **Set environment variables**:
   - Go to Project Settings → Environment Variables
   - Add `GEMINI_API_KEY` with your API key
   - Add any other required environment variables

6. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete

## Post-Deployment Configuration

### 1. Verify Deployment

Your API will be available at:
- **Production**: `https://your-project-name.vercel.app`
- **Preview**: `https://your-project-name-git-branch.vercel.app`

### 2. Test Your API

Test the health endpoint:
```bash
curl https://your-project-name.vercel.app/health
```

Test a query:
```bash
curl "https://your-project-name.vercel.app/query?text=weather%20forecast&location=Mumbai"
```

### 3. Update Mobile App Configuration

Update your Flutter app's API base URL:

```dart
// In your Flutter app's configuration
const String apiBaseUrl = 'https://your-project-name.vercel.app';
```

## Important Notes

### Limitations

1. **Serverless Functions**: Vercel uses serverless functions with:
   - **Timeout**: 10 seconds (Hobby), 60 seconds (Pro), 900 seconds (Enterprise)
   - **Memory**: 1024 MB (Hobby), 3008 MB (Pro), 3008 MB (Enterprise)
   - **Payload**: 4.5 MB (Hobby), 6 MB (Pro), 6 MB (Enterprise)

2. **Cold Starts**: First request may be slower due to serverless cold starts

3. **Dependencies**: Large ML models may not fit in the deployment package

### Recommendations

1. **Use External Services**: For production, consider using:
   - **Qdrant Cloud** for vector database
   - **Redis Cloud** for caching
   - **External ML model hosting** for large models

2. **Optimize Dependencies**: 
   - Remove unused packages from `requirements.txt`
   - Consider using lighter ML models for serverless deployment

3. **Monitor Performance**: 
   - Use Vercel Analytics
   - Monitor function execution times
   - Set up alerts for errors

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check if all dependencies are in `requirements.txt`
   - Ensure Python version compatibility
   - Check for large files that exceed limits

2. **Import Errors**:
   - Verify file paths in `api/index.py`
   - Check if all modules are properly imported

3. **Environment Variables**:
   - Ensure all required env vars are set in Vercel dashboard
   - Check for typos in variable names

4. **Timeout Issues**:
   - Optimize your code for faster execution
   - Consider upgrading to Pro plan for longer timeouts
   - Use external services for heavy computations

### Debugging

1. **Check Vercel Logs**:
   ```bash
   vercel logs
   ```

2. **Local Testing**:
   ```bash
   vercel dev
   ```

3. **Function Logs**: Check Vercel dashboard → Functions tab

## Next Steps

After successful deployment:

1. **Set up custom domain** (optional)
2. **Configure monitoring and alerts**
3. **Set up CI/CD pipeline**
4. **Deploy mobile app updates**
5. **Monitor usage and performance**

## Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Vercel Community**: [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- **Project Issues**: Create an issue in your repository
