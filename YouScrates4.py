#created this file to scrape youtube videos comments and authors and then run a huigging face sentiment analysis model on them
#took me 4 tries haha
#should create a CSV file
#DONEE
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import logging


def scrape_youtube_comments(url, wait_time=15):
    options = webdriver.ChromeOptions()
    options.headless = False
    options.log_level = logging.ERROR
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(url)

        # Handle initial scrolling and comment loading:
        while True:
            current_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(wait_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if current_height == new_height:
                break

        # Collect visible comments, scrolling with lazy loading and "Read More" buttons:
        last_comments = []
        data = []
        id_counter = 1
        while True:
            # Handle comments visible without scrolling:
            comments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "yt-formatted-string#content-text")))
            authors = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "yt-formatted-string.style-scope.ytd-comment-renderer[dir='auto'][style='text-align: left;']")))

            for author, comment_element in zip(authors, comments):
                comment_text = process_comment(comment_element, driver, wait_time)
                data.append([id_counter, author.text.strip(), comment_text])
                id_counter += 1

            # Scroll and wait for new comments and handle "Read More" buttons:
            previous_scroll_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(wait_time)
                new_scroll_height = driver.execute_script("return document.body.scrollHeight")

                # Wait for comments to load after scrolling before processing:
                time.sleep(wait_time)  # Adjust as needed, wait for lazy loading

                # Find new comments and process, including any with "Read More" buttons:
                new_comments = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "yt-formatted-string#content-text")))
                new_authors = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "yt-formatted-string.style-scope.ytd-comment-renderer[dir='auto'][style='text-align: left;']")))

                for new_author, new_comment_element in zip(new_authors, new_comments):
                    if new_comment_element not in comments:  # Check if it's a new comment
                        comment_text = process_comment(new_comment_element, driver, wait_time)
                        data.append([id_counter, new_author.text.strip(), comment_text])
                        id_counter += 1
                        comments.append(new_comment_element)  # Add to list for next iteration

                if new_scroll_height == previous_scroll_height:
                    break
                previous_scroll_height = new_scroll_height

            if comments == last_comments:
                break

            last_comments = comments

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"Error scraping comments: {e}")
        return []
    finally:
        driver.quit()

    return data

def process_comment(comment_element, driver, wait_time):
    if comment_element.text.endswith("..."):
        try:
            more_button = comment_element.find_element(By.CSS_SELECTOR, ".style-scope.ytd-comment-renderer-text-expander")
            more_button.click()
            time.sleep(wait_time)
            comment_text = comment_element.find_element(By.CSS_SELECTOR, "yt-formatted-string#content-text").text
        except (NoSuchElementException, TimeoutException):
            comment_text = comment_element.text
    else:
        comment_text = comment_element.text

    return comment_text

if __name__ == "__main__":
    url = input("Paste the link of the YouTube video you want to scrape comments of: ")
    scraped_data = scrape_youtube_comments(url)
    print("Extracted comments.")

    # Save data to CSV (modify CSV filename if needed)
    df = pd.DataFrame(scraped_data, columns=["ID", "Author", "Comment"])
    df.to_csv("Youtube_comments.csv", index=False)

