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
        tweet_text = ""
        tweet_tags = ""
        tweet_links = ""
        tweet_views = ""
        tweet_likes = ""
        tweet_rts = ""
        tweet_replies = ""
        tweet_metrics = ""
        tweet_bm = ""
        tweet_date = ""        

        while i < 100: #arbitrarily picked 100; unlikely that any tweet spans more than 100 <divs>
            try:
                #tweet text
                tweet_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div/div/span["+str(i)+"]")  # Adjust XPath as needed 
                tweet_text += "\n"+tweet_element.text
                i += 1

            except Exception as e:
                if str(e)[:52] == "Message: no such element: Unable to locate element: ":
                    pass
                else:
                    print(tweet_url, f"An error occurred in text retrieval: {e}")

                i +=1
                continue    

            try:
                #tweet tags (@)
                tweet_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[1]/div/div/div["+str(i-1)+"]/span")  # Adjust XPath as needed 
                tweet_tags += " "+tweet_element.text
                
            except Exception as e:
                if str(e)[:52] == "Message: no such element: Unable to locate element: ":
                    pass
                else:
                    print(tweet_url, f"An error occurred in tag retrieval: {e}")
                continue     

            try:
                #tweet links (url) for tweets containing multiple urls
                tweet_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div/div/div/article/div/div/div[3]/div[1]/div/div/a["+str(i-1)+"]")  # Adjust XPath as needed 
                tweet_links += " "+tweet_element.text
                
            except Exception as e:
                if str(e)[:52] == "Message: no such element: Unable to locate element: ":
                    pass
                else:
                    print(tweet_url, f"An error occurred in multiple link retrieval: {e}")
                continue  

        #if only one link is in the tweet, this section will capture it
        if not tweet_links: 
            try:
                tweet_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div/div/div/article/div/div/div[3]/div[1]/div/div/a")  # Adjust XPath as needed 
                tweet_links += " "+tweet_element.text
                
            except Exception as e:
                if str(e)[:52] == "Message: no such element: Unable to locate element: ":
                    pass
                else:
                    print(tweet_url, f"An error occurred in single link retrieval: {e}")
                pass

        #get tweet metrics
        try:
            tweets = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid=tweetText]')
            stats = driver.find_elements(By.CSS_SELECTOR, 'div[role=group]')
            for idx,stat in enumerate(stats):
                #tweet_metrics = pprint( dict([['tweet',tweets[idx].text]]+[x.split()[::-1] for x in stat.get_attribute('aria-label').split(',')]) )            
                tweet_metrics =  dict([['tweet',tweets[idx].text]]+[x.split()[::-1] for x in stat.get_attribute('aria-label').split(',')]) 
                tweet_views = tweet_metrics['views']
                tweet_likes = tweet_metrics['likes']
                tweet_rts = tweet_metrics['reposts']
                tweet_replies = tweet_metrics['replies']
                tweet_bm = tweet_metrics['bookmarks']               
            
        except Exception as e:
            if str(e)[:52] == "Message: no such element: Unable to locate element: ":
                pass
            else:
                print(tweet_url, f"An error occurred in impressions retrieval: {e}")
            pass            

        #get posting date & time
        try:
            tweet_element = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/section/div/div/div[1]/div/div/article/div/div/div[3]/div[4]/div/div[1]/div/div[1]/a")
            
            tweet_date += " "+tweet_element.text
            
        except Exception as e:
            if str(e)[:52] == "Message: no such element: Unable to locate element: ":
                pass
            else:
                print(tweet_url, f"An error occurred in date retrieval: {e}")
            pass  
        
        return tweet_text, tweet_tags, tweet_links, tweet_views, tweet_likes, tweet_rts, tweet_replies, tweet_bm, tweet_date

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        driver.quit()

def remove_non_utf8(input_string):
    # Encode the string to bytes, ignoring errors, then decode back to string
    return input_string.encode('utf-8', 'ignore').decode('utf-8', 'ignore')

timestamp = datetime.today().strftime('%Y%m%d%H%M')
print( "START TIME: ", timestamp)

with open("tweet_list.csv", "r") as csvfile: #file contains a header
    reader = csv.reader(csvfile)
    counts = list(reader)[1:]

result = list(filter(None, counts))
tweet_details_dictList = []

for tweet in result:
    try:
        result = scrape_tweet(tweet[0])
        tweet_text = remove_non_utf8(result[0].replace("\n\n",". ").replace("\n"," ").replace(",",";")).replace("â€™","'").replace("â€œ",'"').replace("â€",'"') #replace new lines with a full-stop and commas with semi-colons to resolve formatting issues when saving as csv
        tweet_tags = result[1]
        tweet_links = result[2]
        tweet_views = result[3] 
        tweet_likes = result[4]
        tweet_rts = result[5]
        tweet_replies = result[6]
        tweet_bm = result[7]
        tweet_date = result[8].replace("·",". ").replace(","," ").replace("\n"," ").replace("Last edited","")
          
        time.sleep(3) #extra buffer to prevent rate limit issues
    except:
        print("Failed to grab tweet %s" % tweet[0])
        continue
    
    if tweet_text:
        tweet_text_dict = {}
        tweet_text_dict['id']=tweet[0][-19:]
        tweet_text_dict['text']=tweet_text[1:] #[1:] removes the leading space caused by the replace operators in line 102
        tweet_text_dict['tags'] = tweet_tags[1:]
        tweet_text_dict['links'] = tweet_links[1:]
        tweet_text_dict['views'] = tweet_views   
        tweet_text_dict['likes'] = tweet_likes 
        tweet_text_dict['rts'] = tweet_rts 
        tweet_text_dict['replies'] = tweet_replies 
        tweet_text_dict['bookmarks'] = tweet_bm 
        tweet_text_dict['date'] = tweet_date              
        
        tweet_details_dictList.append(tweet_text_dict)

    else:
        print("Failed to retrieve tweet text %s" % tweet[0])

filename = timestamp + '_tweet-details.csv'

#print(tweet_details_dictList)
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
