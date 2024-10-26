from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import os

app = Flask(__name__)

# Set the path to the GeckoDriver
geckodriver_path = os.path.join(os.getcwd(), "geckodriver.exe")  # Ensure it's in the current working directory
service = Service(executable_path=geckodriver_path)

def scrape_google_search(query):
    options = Options()
    options.headless = False  # Set to True if you want to run without opening a browser window
    
    # Specify the path to the Firefox binary if it's not in the default location
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"  # Change this path if necessary

    driver = webdriver.Firefox(service=service, options=options)

    results = []
    
    try:
        # Go to Google
        driver.get("https://www.google.com")
        
        # Wait for the search box and enter the query
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.submit()
        
        # Wait for the search results to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search")))

        # Get multiple search result titles and URLs
        search_results = driver.find_elements(By.XPATH, "//h3")

        for result in search_results:
            title = result.text
            link = result.find_element(By.XPATH, "..").get_attribute("href")  # Get the link from the parent element
            results.append({"title": title, "link": link})
    finally:
        driver.quit()
    
    return results

@app.route('/')
def home():
    return '''
        <form action="/scrape" method="post">
            <label>Enter a search term:</label>
            <input type="text" name="query">
            <button type="submit">Search</button>
        </form>
    '''

@app.route('/scrape', methods=['POST'])
def scrape():
    query = request.form.get("query")
    if not query:
        return "No query provided", 400

    # Call the scraping function
    search_results = scrape_google_search(query)

    # Render results using an HTML template
    return render_template('results.html', query=query, results=search_results)

if __name__ == '__main__':
    app.run(debug=True)
