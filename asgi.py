import uvicorn

from app import create_app
from config import settings

api = create_app(settings)

if __name__ == "__main__":
    uvicorn.run("asgi:api", host="0.0.0.0", port=8181, reload=True)
