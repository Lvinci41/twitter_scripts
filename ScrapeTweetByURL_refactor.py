from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import csv
from datetime import datetime
from pprint import pprint
import random

def remove_non_utf8(input_string):
    # Encode the string to bytes, ignoring errors, then decode back to string
    return input_string.encode('utf-8', 'ignore').decode('utf-8', 'ignore')

def fix_metrics_dict(metrics_dict, item_name, item_name_plural=""):
    if type(metrics_dict) != dict:
        print('Invalid metrics_dict: dict expected, got ',type(path))
        return metrics_dict
    if type(item_name) != str:
        print('Invalid item_name: string expected, got ',type(item_name))
        return metrics_dict
    if type(item_name_plural) != str:
        print('Invalid item_name_plural: string expected, got ',type(item_name_plural))
        return metrics_dict    

    if item_name_plural=="":
        item_name_plural = item_name+"s"

    if item_name_plural not in metrics_dict:
        if item_name not in metrics_dict:
            metrics_dict[item_name_plural] = "0"
        else:
            metrics_dict[item_name_plural] = metrics_dict[item_name]
            del metrics_dict[item_name]
        
    return metrics_dict
                     
def xpath_lookup(path, driver):
    if type(path) != str:
        print('Invalid path: string expected, got ',type(path))
        return ""

    try:
        return driver.find_element(By.XPATH, path).text
        
    except Exception as e:
        if str(e)[:52] == "Message: no such element: Unable to locate element: ":
            return ""
        else:
            #print(tweet_url, f"An error occurred in tag retrieval: {e}")
            print(f"An error occurred in tag retrieval: {e}")
            return ""      

def xpath_lookup_i(path, iterator, iterator_loc, driver):
    if type(iterator) != int:
        print('Invalid iterator: int expected, got ',type(iterator))    
        return ""        
    if type(iterator_loc) != int:
        print('Invalid iterator_loc: int expected, got ',type(iterator_loc))  
        return ""

    return xpath_lookup(path[:iterator_loc]+str(iterator)+path[iterator_loc:], driver)

def css_selector_lookup(css_element_1, css_element_2, css_attribute, driver):    
    if type(str(css_element_1)) != str:
        print('Invalid css_element_1: string expected, got ',type(css_element_1))
        return ""
    if type(str(css_element_2)) != str:
        print('Invalid css_element_2: string expected, got ',type(css_element_2))    
        return ""        
    if type(str(css_attribute)) != str:
        print('Invalid css_attribute: string expected, got ',type(css_attribute))  
        return ""    

    try:
        tweets = driver.find_elements(By.CSS_SELECTOR, css_element_1)
        stats = driver.find_elements(By.CSS_SELECTOR, css_element_2)
        for idx,stat in enumerate(stats):
            attribute_value = stat.get_attribute(css_attribute)
            if attribute_value is None:
                # Handle the case where attribute_value is None
                print(f"Warning: No value found for attribute '{css_attribute}' at index {idx}.")
                continue

            tweet_css_dict = dict([['tweet', tweets[idx].text]] + [x.split()[::-1] for x in attribute_value.split(',')])

        return tweet_css_dict
        
    except Exception as e:
        if str(e)[:52] == "Message: no such element: Unable to locate element: ":
            return ""
        else:
            #print(tweet_url, f"An error occurred in impressions retrieval: {e}")
            print(f"An error occurred in impressions retrieval: {e}")
            return {"tweet":"0","views":"0","replies":"0","reposts":"0","likes":"0", "bookmarks":"0", "bookmark":"0"}  

def scrape_tweet(tweet_url):
    # Set up the Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no GUI)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open the tweet URL
        driver.get(tweet_url)
        time.sleep(8)  # Wait for the page to load

        i=1
        tweet_text=tweet_tags=tweet_links=tweet_date  = ""       

        while i < 100: #arbitrarily picked 100; unlikely that any tweet spans more than 100 <divs>
            tweet_text += ". "+xpath_lookup_i("/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div/div/span[]", i, 135, driver)
            tweet_text += ". "+xpath_lookup_i("/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div[]/div/article/div/div/div[3]/div[1]/div/div/span", i, 88, driver)
            tweet_text += ". "+xpath_lookup_i("/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div[1]/div/article/div/div/div[3]/div[1]/div/div/span[]", i, 138, driver)     
            tweet_tags += " "+xpath_lookup_i("/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div/div/div[]/span", i, 134, driver)                      
            tweet_links += " "+xpath_lookup_i("/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div/div/div/article/div/div/div[3]/div[1]/div/div/a[]", i, 129, driver)
            i+=1
        
        if not tweet_links: 
            tweet_links = xpath_lookup("/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div/div/div/article/div/div/div[3]/div[1]/div/div/a", driver)

        tweet_metrics = css_selector_lookup("div[data-testid=tweetText]", "div[role=group]", "aria-label", driver) 

        if "views" not in tweet_metrics: #case where views is not captured by css_selector
            #tweet_metrics["views"] = xpath_lookup("/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div[1]/div/article/div/div/div[3]/div[4]/div/div[1]/div/div[3]/span/div/span/span/span", driver)
            tweet_metrics["views"] = xpath_lookup("/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div[1]/div/article/div/div/div[3]/div[4]/div/div[1]/div/div[3]/span/div/span/span", driver)
        
        tweet_date = xpath_lookup("/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[4]/div/div[1]/div/div[1]/a", driver)
        
        return tweet_text, tweet_tags, tweet_links, tweet_date, tweet_metrics 

    except Exception as e:
        print(f"An error occurred: {e}")
        return ""
    
    finally:
        driver.quit()

timestamp = datetime.today().strftime('%Y%m%d%H%M')
print( "START TIME: ", timestamp)

with open("tweet_list6.csv", "r") as csvfile: #file contains a header
    reader = csv.reader(csvfile)
    counts = list(reader)[1:]

tweet_list = list(filter(None, counts))
tweet_details_dictList = []

for tweet in tweet_list:
    result = scrape_tweet(tweet[0])
    expected_keys = ["views", "likes", "reposts", "replies", "bookmarks"]
    expected_keys_dict = {"views":"view", "likes":"like", "reposts":"repost", "replies":"reply", "bookmarks":"bookmark"}
    tweet_metrics_fixed = result[4]
    for key in expected_keys_dict:
        if key not in tweet_metrics_fixed:
            tweet_metrics_fixed = fix_metrics_dict(tweet_metrics_fixed, expected_keys_dict[key], key)
    
    tweet_text = remove_non_utf8(result[0].replace("\n\n",". ").replace("\n"," ").replace(",",";")).replace("â€™","'").replace("â€œ",'"').replace("â€",'"').replace("â€”", '"') #replace new lines with a full-stop and commas with semi-colons to resolve formatting issues when saving as csv
    tweet_tags = result[1].replace("\n","")
    tweet_links = result[2].replace("\n","")
    tweet_date = result[3].replace("·",". ").replace(","," ").replace("\n"," ").replace("Last edited","")  
    time.sleep(random.randint(2,25)) #extra buffer to prevent rate limit issues

    if tweet_text:
        tweet_text_dict = {}
        tweet_text_dict['url']=tweet[0]
        tweet_text_dict['text']=tweet_text[2:] 
        tweet_text_dict['tags'] = tweet_tags[1:]
        tweet_text_dict['links'] = tweet_links[1:]
        tweet_text_dict['views'] = tweet_metrics_fixed["views"]   
        tweet_text_dict['likes'] = tweet_metrics_fixed["likes"] 
        tweet_text_dict['rts'] = tweet_metrics_fixed["reposts"] 
        tweet_text_dict['replies'] = tweet_metrics_fixed["replies"] 
        tweet_text_dict['bookmarks'] = tweet_metrics_fixed["bookmarks"] 
        tweet_text_dict['date'] = tweet_date          
        tweet_details_dictList.append(tweet_text_dict)

    else:
        print("Failed to retrieve tweet text %s" % tweet[0])

filename = timestamp + '_tweet-details.csv'
with open(filename, 'w', encoding='utf-8') as file: 
    # Write the header 
    header = ','.join(tweet_details_dictList[0].keys())  # Get the keys from the first dictionary 
    file.write(header + '\n')  # Write header followed by a newline 
     
    # Write the data 
    for entry in tweet_details_dictList: 
        row = ','.join(str(entry[key]) for key in entry)  # Convert each value to string and join with commas 
        file.write(row + '\n')  # Write each row followed by a newline 
 
print(f"Data exported to {filename}")   
print( "END TIME: ", datetime.today().strftime('%Y%m%d%H%M'))      