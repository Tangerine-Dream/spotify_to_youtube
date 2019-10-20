#python script that takes a spotify playlist and creates a youtube playlist

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import requests, re, json

#get songs and artist names from spotify link
s = requests.session()
r = s.get('open.spotify.com/somethingsomething')
p = re.compile(r'Spotify\.Entity = (.*?);')
data = json.loads(p.findall(r.text)[0])

#truncate playlist name if greater than 150 char per youtube naming limit
playlist_name = data['name'][:150] if len(data['name'][:150]) > 150 else data['name'][:150]
search_terms = []

#parse to find the track and artist names
for idx in range(0,len(data['tracks']['items'])):

    cur_data = data['tracks']['items'][idx]
    track_info = cur_data['track']
    track_name = track_info['name']

    artist_num = len(track_info['artists'])
    artist_name = ''
    if artist_num > 1:
        for i in range(0,artist_num):
            artist_name += ' '+ track_info['artists'][i]['name']
    else:
        artist_name = track_info['album']['artists'][0]['name']
    search_terms.append(track_name + ' ' +artist_name)


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--window-size=1920,1080")  
# optional ublock extension while opening chrome
# chrome_options.add_extension(r'path\to\extension\uBlock-Origin_v1.22.4.crx')
driver = webdriver.Chrome(
    executable_path= r'path\to\chromedriver.exe', options=chrome_options)


driver.get('https://www.youtube.com')
login = "//*[@id='buttons']/ytd-button-renderer/a"

try:
    login_present = EC.element_to_be_clickable((By.XPATH,login))
    WebDriverWait(driver,5).until(login_present)
    button = driver.find_element_by_xpath(login)
    ActionChains(driver).move_to_element(button).click(button).perform()
except TimeoutException:
    print("Timed out")

try:
    username_present = EC.presence_of_element_located((By.ID,'identifierId'))
    WebDriverWait(driver,5).until(username_present)
    username = driver.find_element_by_id('identifierId')
    username.send_keys('youryoutubeemail@provider.com')
    username.send_keys(Keys.ENTER)
except TimeoutException:
    print("Timed out")

try: 
    pw_present = EC.presence_of_element_located((By.NAME,'password'))
    WebDriverWait(driver,5).until(pw_present)
    pw = driver.find_element_by_name('password')
    pw.send_keys('youtubepassword')
    pw.send_keys(Keys.ENTER)
except TimeoutException:
    print("Timed out")


#loops through every song/artist term and adds to playlist
for idx,search in enumerate(search_terms):
    try:
        searchBar_xpath = "/html/body/ytd-app/div/div/ytd-masthead/div[3]/ytd-searchbox/form/div/div[1]/input"
        searchBar_present = EC.element_to_be_clickable((By.XPATH,searchBar_xpath))
        
        WebDriverWait(driver,20).until(searchBar_present)
        searchBar = driver.find_element_by_xpath(searchBar_xpath)
        
        searchBar.clear()
        driver.implicitly_wait(1)
        print(search)
        searchBar.send_keys(search)
        searchBar.send_keys(Keys.ENTER)
    except TimeoutException:
        print("Timed out search bar")
    
    try:
        firstLink = '/html/body/ytd-app/div/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-video-renderer[1]/div[1]/div/div[1]/div'
        link_present = EC.element_to_be_clickable((By.XPATH,firstLink))
        WebDriverWait(driver,5).until(link_present)
        button = driver.find_element_by_xpath(firstLink)
        ActionChains(driver).move_to_element(button).click(button).perform()
    except TimeoutException:
        print("Timed out")
    
    try:
        saveLink = '//*[@id="top-level-buttons"]/ytd-button-renderer[2]/a'
        save_present = EC.element_to_be_clickable((By.XPATH,saveLink))
        WebDriverWait(driver,5).until(save_present)
        button = driver.find_element_by_xpath(saveLink)
        ActionChains(driver).move_to_element(button).click(button).perform()
    except TimeoutException:
        print("Timed out save link")   
    
    if idx == 0:
        # create new playlist
        try:
            newPlaylist = '//*[@id="actions"]/ytd-add-to-playlist-create-renderer'
            newPlaylistPresent = EC.element_to_be_clickable((By.XPATH,newPlaylist))
            WebDriverWait(driver,5).until(newPlaylistPresent)
            button = driver.find_element_by_xpath(newPlaylist)
            ActionChains(driver).move_to_element(button).click(button).perform()
            try:
                newPlaylist = '//*[@id="input-2"]/input'
                newPlaylistPresent = EC.element_to_be_clickable((By.XPATH,newPlaylist))
                WebDriverWait(driver,5).until(newPlaylistPresent)
                field = driver.find_element_by_xpath(newPlaylist)
                field.send_keys(playlist_name)
                create = '//*[@id="actions"]/ytd-button-renderer'
                button = driver.find_element_by_xpath(create)
                ActionChains(driver).move_to_element(button).click(button).perform()

            except TimeoutException:
                print("New playlist creation failed")

        except TimeoutException:
            print("New playlist failed")
        
    else:

        try: 
            button_xpath = '//*[@id="playlists"]/ytd-playlist-add-to-option-renderer[2]'
            
            button_present = EC.element_to_be_clickable((By.XPATH,button_xpath))
            WebDriverWait(driver,20).until(button_present)
            button = driver.find_element_by_xpath(button_xpath)
            ActionChains(driver).move_to_element(button).click(button).perform()
        except TimeoutException:
            print('add to youtube failed')
            
    ActionChains(driver).send_keys(Keys.ESCAPE).perform()

        

