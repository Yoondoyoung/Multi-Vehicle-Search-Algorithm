from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from search_algorithm import search_algorithm
import uvicorn

app = FastAPI(
    title="Neighbor Vehicle Search API",
    description="API for finding optimal vehicle storage locations",
    version="1.0.0"
)


class Vehicle(BaseModel):
    length: int = Field(..., description="Vehicle length in feet")
    quantity: int = Field(..., description="Number of vehicles of this dimension", ge=1, le=5)


@app.get("/")
async def root():
    return {
        "message": "Neighbor Vehicle Search API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "search": "POST /search"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/search")
async def search(vehicles: List[Vehicle]):
    
    try:
        request_data = [{"length": v.length, "quantity": v.quantity} for v in vehicles]
        results = search_algorithm(request_data)
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

