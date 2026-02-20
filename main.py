from selenium import webdriver
from fake_useragent import UserAgent
from fastapi import FastAPI
from urllib.parse import unquote
import httpx
import os
from fastapi.staticfiles import StaticFiles

IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Create a FastAPI application instance
app = FastAPI()

app.mount("/images", StaticFiles(directory=IMAGE_DIR), name="images")

# create ChromeOptions object
options = webdriver.ChromeOptions()
options.add_argument('--headless')

# Define a GET endpoint at the root URL ("/")
@app.get("/get-content/{url}")
def read_root(url):
    # Generate a random User-Agent
    user_agent = UserAgent().random
    options.add_argument(f"user-agent={user_agent}")

    # Set up WebDriver
    driver = webdriver.Chrome(options=options)

    # Open a webpage
    driver.get(unquote(unquote(url)))
    
    content = driver.page_source

    driver.quit()
    
    return {"content": content}

@app.get("/download-favicon/{id}/{url}")
async def download_favicon(id, url):
    """Download the image from the source URL and save it to the server."""
    async with httpx.AsyncClient() as client:
        response = await client.get(unquote(unquote(url)), follow_redirects=True)
        response.raise_for_status()

    path = os.path.join(IMAGE_DIR, id + '_favicon.ico')
    with open(path, "wb") as f:
        f.write(response.content)

    return {
        'path': '/' + path
    }