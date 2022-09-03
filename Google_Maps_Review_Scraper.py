#!/usr/bin/env python
# coding: utf-8

# In[1]:
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
import dateparser

# In[32]:


chrome_driver_path = r"Passing the location of Chromewebdriver.exe here"
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(executable_path=chrome_driver_path,options=options)
#add your google maps address here
url = 'https://www.google.com/maps/place/.....'

driver.get(url)
time.sleep(5)
print("Page Title is : %s" %driver.title)


# In[33]:


#first accepting all cookies before moving to our actual search
driver.find_element(By.XPATH, "//span[text()='Accept all']").click()
time.sleep(1)

# we now need to click on the reviews option where total number of reviews are mentioned ex: 55k reviews
driver.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/div[2]/span[2]/span[1]/button').click()
time.sleep(1)

# we now need to click on the sort option and then onto most relevant option to fetch the reviews, two stage process
driver.find_element(By.XPATH, "//button[@aria-label='Sort reviews']").click()
time.sleep(5)

# Sorting the latest reviews in the order
# Please note that we can change this indexing to 0,1,2,3 as per our choice, like if we want to fetch the latest or most relevant reviews etc
wait = WebDriverWait(driver, 20)
wait.until(EC.visibility_of_element_located((By.XPATH, "//li[@data-index='1']"))).click()


# In[34]:

# Get scroll height, how many review pages we want to scroll
SCROLL_PAUSE_TIME = 14
last_height = driver.execute_script("return document.body.scrollHeight")
number = 0
while True:
    number = number+1

    # Scroll down to bottom
    
    ele = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[10]')
    driver.execute_script('arguments[0].scrollBy(0, 5000);', ele)

    # Wait to load page

    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    print(f'last height: {last_height}')

    ele = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[10]')

    new_height = driver.execute_script("return arguments[0].scrollHeight", ele)

    print(f'new height: {new_height}')

    if number == 5:
        break

    if new_height == last_height:
        break

    print('cont')
    last_height = new_height


# In[35]:
item = driver.find_elements(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[10]')
# In[36]:
# instantiating four empty lists to store names, stars, reviews and when was the review posted
name_list = []
stars_list = []
review_list = []
duration_list = []
for i in item:
    button = i.find_elements(By.TAG_NAME,'button')
    for m in button:
        if m.text == "More":
            m.click()
    time.sleep(5)

    name = i.find_elements(By.CLASS_NAME,"d4r55") # standard class names that can be found while inspecting elements - Right click on the name and select inspect element
    stars = i.find_elements(By.CLASS_NAME,"kvMYJc") # standard class names that can be found while inspecting elements
    review = i.find_elements(By.CLASS_NAME,"wiI7pd")# standard class names that can be found while inspecting elements
    duration = i.find_elements(By.CLASS_NAME,"rsqaWe")# standard class names that can be found while inspecting elements

    for j,k,l,p in zip(name,stars,review,duration):
        name_list.append(j.text)
        duration_list.append(p.text)
        stars_list.append(k.get_attribute("aria-label"))
        review_list.append(l.text)


# In[37]:
google_reviews = pd.DataFrame(
    {'name': name_list,
     'rating': stars_list,
     'review': review_list,
     'duration': duration_list})
# using dateparser to convert the 'x months/years ago' to a proper date
google_reviews['date_of_review'] = google_reviews['duration'].apply(lambda x :dateparser.parse(x).strftime('%Y-%m-%d'))

#removing the word "Star" or "Stars" from the rating column and just fetching the value of rating
google_reviews['rating'] = google_reviews.rating.str.extract('(\d+)').astype(int)

# dropping cols that we dont need
google_reviews.drop(['name','duration'],axis=1, inplace=True)

# In[38]:
google_reviews.to_excel('google_reviews.xlsx',index=False)

