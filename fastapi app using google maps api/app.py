# FastAPI code using Google Maps API

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import requests
import sqlite3

app = FastAPI()
conn = sqlite3.connect('company_details.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        country TEXT NOT NULL,
        address TEXT
    )
''')

def get_company_address(company_name: str, country: str) -> str:
    api_key = "AIzaSyBqySY_MU_b7K4IyUN2SnB4e2yNL2kZFus"
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        "input": f"{company_name} {country}",
        "inputtype": "textquery",
        "fields": "formatted_address",
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "candidates" in data and data["candidates"]:
        return data["candidates"][0]["formatted_address"]
    else:
        return "Address not found"

html_form = """
<form method="post">
    <label for="company_name">Company Name:</label><br>
    <input type="text" id="company_name" name="company_name"><br>
    <label for="country">Country:</label><br>
    <input type="text" id="country" name="country"><br><br>
    <button type="submit">Get Address</button>
</form>
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return html_form

@app.post("/", response_class=HTMLResponse)
async def process_form(request: Request, company_name: str = Form(...), country: str = Form(...)):
    address = get_company_address(company_name, country)

    cursor.execute('''
        INSERT INTO companies (name, country, address) VALUES (?, ?, ?)
    ''', (company_name, country, address))
    conn.commit()

    return f"<h2>Company Address:</h2><p>{address}</p>"
