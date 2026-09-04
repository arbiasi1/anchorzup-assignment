from fastapi import FastAPI
from .api import router

app = FastAPI(
    title="Rule-Based Content Filter",
    version="1.0.0",
    description="Store matching rules and annotate text with highlights and tooltips.",
)
app.include_router(router)


@app.get("/", include_in_schema=False)
def root():
    return {"name": app.title, "docs": "/docs", "health": "/api/health"}
