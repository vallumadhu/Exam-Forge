from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.pdf_routers import router as pdf_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    pdf_router,
    prefix="/pdf",
    tags=["Notes"]
)

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind')
    parser.add_argument('--port', type=int, default=6871, help='Port to bind')
    
    args = parser.parse_args()
    
    print(f"Starting FastAPI server on {args.host}:{args.port}")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )