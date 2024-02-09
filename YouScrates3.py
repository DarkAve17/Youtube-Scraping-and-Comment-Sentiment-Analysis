from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(url)

        # Scroll down to load more comments
        while True:
            current_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)  # Adjust as needed
            new_height = driver.execute_script("return document.body.scrollHeight")

            if current_height == new_height:
                break

        # Handle "Read More" buttons
        expand_long_comments(driver)

        # Wait for final comment  to load
        comment_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                                        "yt-formatted-string#content-text.style-scope.ytd-comment-renderer")))
        author_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                                        "yt-formatted-string.style-scope.ytd-comment-renderer.style-scope.ytd-comment-renderer[dir='auto'][style='text-align: left;']")))

        # Extract and process comments
        comments = [expand_long_comments(element) for element in comment_elements]
        authors = [element.text.strip() for element in author_elements]

        # Create DataFrame with ID column
        id_counter = 1
        data = []
        for author, comment in zip(authors, comments):
            data.append([id_counter, author, comment])
            id_counter += 1

        df = pd.DataFrame(data, columns=["ID", "Author", "Comment"])

        # Save to CSV
        df.to_csv("Youtube_comments.CSV", index=False)

    except (NoSuchElementException, TimeoutException) as e:
        logging.error(f"Error scraping comments: {e}")
    finally:
        driver.quit()


def expand_long_comments(driver):
    # Find and click "Read More" buttons, wait for loading
    read_more_buttons = driver.find_elements(By.CSS_SELECTOR,
                                            "yt-formatted-string.style-scope.ytd-comment-renderer.style-scope.ytd-comment-renderer[dir='auto'][style='text-align: left;'] + div.style-scope.ytd-comment-renderer-text-expander")
    for button in read_more_buttons:
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(button))
            button.click()
            time.sleep(2)  # Adjust as needed
        except TimeoutException:
            pass  # Log or handle timeout gracefully


def expand_truncated_comment(comment_element):
    # Check if comment ends with "... (Show more)" and click if so
    if comment_element.text.endswith("... (Show more)"):
        try:
            # Find and click "Show more" button within the element
            more_button = comment_element.find_element(By.CSS_SELECTOR, ".style-scope.ytd-comment-renderer-text-expander")
            more_button.click()
            time.sleep(1)  # Adjust as needed
            # Get the expanded comment text
            expanded_text = comment_element.find_element(By.CSS_SELECTOR, "yt-formatted-string#content-text").text
            return expanded_text
        except (NoSuchElementException, TimeoutException):
            return comment_element.text
    else:
        return comment_element.text


if __name__ == "__main__":
    url = input("Paste the link of the YouTube video you want to scrape comments of: ")
    scraped_data = scrape_youtube_comments(url)
    print("Extracted comments.")
    #for author, comment in scraped_data:
    #    print(f"{author}  ||  {comment}")