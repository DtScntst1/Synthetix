Write-Host "InsightGraph Başlatılıyor..." -ForegroundColor Green

# Start Backend
Write-Host "1. Arka uç (FastAPI) başlatılıyor..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command `"cd backend; pip install -r requirements.txt; uvicorn app.main:app --reload`""

# Wait a few seconds for backend to initialize
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "2. Ön Yüz (Next.js) başlatılıyor..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit -Command `"cd frontend; npm run dev`""

Write-Host "Her iki sunucu da ayrı pencerelerde başlatıldı! Lütfen Chrome'da http://localhost:3000 adresine gidin." -ForegroundColor Green
