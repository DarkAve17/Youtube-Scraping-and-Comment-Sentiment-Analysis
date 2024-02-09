#file to scrape comments of a youtube video link provided

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import logging
import csv



def scrape_youtube_comments(url):
    
    options = Options()
    options.headless = False  
    options.log_level = logging.ERROR

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)  # Set explicit wait timeout

    try:
        driver.get(url)

        # Scroll down to load more comments
        while True:
            current_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(15)  
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if current_height == new_height:
                time.sleep(7)
                break

        # Wait for specific comment elements to load
        comment_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "yt-formatted-string#content-text.style-scope.ytd-comment-renderer")))
        author_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "yt-formatted-string.style-scope.ytd-comment-renderer.style-scope.ytd-comment-renderer[dir='auto'][style='text-align: left;']")))

        comments = [element.text.strip() for element in comment_elements]
        authors = [element.text.strip() for element in author_elements]
        #print(authors)
        #print(comments)


        file =  open("Youtube_comments.CSV", "w",)
        writer = csv.writer(file)
        writer.writerow(["ID","Author","Comment"])
        id_counter = 1  # Start with id_counter 1

        #for author, comment in zip(authors, comments):
            #writer.writerow([id_counter, author.text, comment.text])
            #id_counter += 1
        # Create DataFrame and write content to CSV
        df = pd.DataFrame({'Author': authors, 'Comment': comments})
        df.to_csv("Youtube_comments.CSV", index=False)

        
        
        return list(zip(authors, comments))

    except NoSuchElementException:
        logging.error("Failed to find comment elements.")
        return []

    finally:
        driver.quit()



if __name__ == "__main__":
    url = input("Paste the link of the YouTube video you want to scrape comments of: ")
    scraped_data = scrape_youtube_comments(url)
    print("Extracted comments:")
    for author, comment in scraped_data:
        print(f"{author}  ||  {comment}")

#def get_video_link(url):
    #"""Extracts the video link from the input URL."""
    ## Apply your logic to extract the video link from the URL
    ## (assuming it's already present in the URL structure)
    #video_id = url.split("=")[1]  # Example extraction
    #return f"https://www.youtube.com/watch?v={video_id}"

