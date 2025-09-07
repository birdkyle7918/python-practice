import uvicorn

if __name__ == "__main__":
    uvicorn.run("tg_crawler.main:app", host="0.0.0.0", port=8444, reload=True)
