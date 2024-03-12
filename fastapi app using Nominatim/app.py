from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import requests
import sqlite3


app = FastAPI(debug=True)
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
conn.commit()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return """
        <html>
            <head>
                <title>Company Address Finder</title>
            </head>
            <body>
                <h1>Enter Company Name and Country</h1>
                <form method="post">
                    <label for="company">Company Name:</label><br>
                    <input type="text" id="company" name="company"><br>
                    <label for="country">Country:</label><br>
                    <input type="text" id="country" name="country"><br><br>
                    <button type="submit">Submit</button>
                </form>
            </body>
        </html>
    """

@app.post("/", response_class=HTMLResponse)
async def process_form(request: Request, company: str = Form(...), country: str = Form(...)):
    url = f"https://nominatim.openstreetmap.org/search?q={company}, {country}&format=json&limit=1"
    response = requests.get(url, verify=False)
    data = response.json()
    if data:
        address = data[0]['display_name']
    else:
        address = "Address not found"
    
    cursor.execute('''
        INSERT INTO companies (name, country, address) VALUES (?, ?, ?)
    ''', (company, country, address))
    conn.commit()

    return f"""
        <html>
            <head>
                <title>Company Address Finder</title>
            </head>
            <body>
                <h1>Address for {company} in {country}</h1>
                <p>{address}</p>
                <a href="/">Go Back</a>
            </body>
        </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
