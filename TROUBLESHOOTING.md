# Troubleshooting Guide

## Error: "Analysis failed. Is Ollama running?"

This error has been FIXED. The app now works WITHOUT Ollama using regex-based extraction.

### Solution Steps:

1. **Check if backend is running:**
   ```bash
   python check_backend.py
   ```

2. **If backend is NOT running:**
   - Double-click `start-backend.bat`
   - OR manually:
     ```bash
     cd backend
     venv\Scripts\activate
     uvicorn app.main:app --reload --port 8000
     ```

3. **If backend IS running but frontend shows error:**
   - Restart the frontend:
     - Close the frontend terminal (Ctrl+C)
     - Double-click `start-frontend.bat` again
   - OR manually:
     ```bash
     cd frontend
     npm run dev
     ```

4. **Check browser console:**
   - Press F12 in your browser
   - Look at the Console tab
   - Check for any red errors

## Common Issues:

### Issue 1: Port Already in Use
**Error:** `Address already in use`

**Solution:**
- Backend: Change port in `start-backend.bat` (8000 → 8001)
- Frontend: Vite will auto-assign a different port

### Issue 2: No Skills Extracted
**Error:** `Could not extract any skills from resume`

**Solution:**
- Make sure your resume contains technical skills
- Supported skills: Python, JavaScript, React, Docker, SQL, etc.
- File must be readable (PDF, DOCX, or TXT)

### Issue 3: CORS Error
**Error:** `Access-Control-Allow-Origin`

**Solution:**
- Backend already has CORS enabled for all origins
- Restart both backend and frontend
- Clear browser cache (Ctrl+Shift+Delete)

### Issue 4: Module Not Found
**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

## Testing the Fix:

1. **Start backend:**
   ```bash
   start-backend.bat
   ```
   Wait for: "Uvicorn running on http://127.0.0.1:8000"

2. **Check backend health:**
   ```bash
   python check_backend.py
   ```
   Should show: "✅ Backend is RUNNING!"

3. **Start frontend:**
   ```bash
   start-frontend.bat
   ```
   Wait for: "Local: http://localhost:3000"

4. **Test in browser:**
   - Open http://localhost:3000
   - Upload resume and JD
   - Click "FORGE MY PATHWAY"
   - Should see results!

## Still Having Issues?

Check the terminal output for detailed error messages. The backend now prints:
- File text length
- Number of skills extracted
- Detailed error messages

Look for lines starting with:
- `[DEBUG]` - Information
- `[INFO]` - Status updates
- `[WARN]` - Warnings
- `[ERROR]` - Errors
