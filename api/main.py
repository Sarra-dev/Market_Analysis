from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import jobs, stats

app = FastAPI(
    title="Market Analysis API",
    description="IT Job Market Analysis API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(stats.router)

@app.get("/")
def root():
    return {"message": "Market Analysis API is running ✅"}