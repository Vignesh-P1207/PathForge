@echo off
echo Starting PathForge Frontend...
cd frontend

if not exist node_modules (
    echo Installing npm dependencies...
    npm install
)

echo Starting Vite dev server...
npm run dev
