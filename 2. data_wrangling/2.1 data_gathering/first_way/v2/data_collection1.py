from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time
import numpy as np 

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)      # Now service is not required
wait = WebDriverWait(driver, 10)
time.sleep(5)

cid = np.load('candidate_id.npy')
# test_id = [339933, 341131, 339610]

# 1. Open the file ONCE outside the loop in append mode ("a")
with open("combined_election_2082_v2.html", "a", encoding="utf-8") as file:


    # This automatically gives you a count starting at 1
    for count, i in enumerate(cid, start=1):

        linkz = f"https://nepalvotes.live/candidate/{i}"
        driver.get(linkz)
        
        # Wait for JavaScript content to finish loading
        time.sleep(1) 

        # 2. Grab the full HTML structure
        html_content = driver.page_source

        # 3. Append the HTML content to the single open file
        # Adding a separator comment makes it easier to parse or read later
        file.write(f"\n<!-- START CANDIDATE {i} -->\n")
        file.write(html_content)
        file.write(f"\n<!-- END CANDIDATE {i} -->\n")
            
        print(f"Appended candidate {i} for the {count}th time to a single HTML file")

        # Break the loop after the 100th iteration
        if count == 100:
            break

input("Press Enter to close browser...")
driver.quit()