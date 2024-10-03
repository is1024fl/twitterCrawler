from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from pathlib import Path

class TwitterCrawler:

	LOGIN_PAGE = "https://twitter.com/i/flow/login"
	PAUSE_TIME = 3

	def __init__(self, show_screen=True):

		# set up driver
		options = Options()
		if not show_screen:
			options.add_argument("--disable-notifications")
		
		driver_dir = Path(ChromeDriverManager().install()).parent
		self.driver = webdriver.Chrome(service=Service(Path(driver_dir, "chromedriver.exe")), options=options)

	def quit(self):
		self.driver.quit()

	def login(self, user_info=None):

		if not user_info:
			with open('.env') as f:
				user_info = json.load(f)
		
		self.driver.get(self.LOGIN_PAGE)
		WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@autocomplete='username']")))

		username_input = self.driver.find_elements(By.XPATH, "//*[@autocomplete='username']")[0]
		username_input.send_keys(user_info["username"])
		username_input.send_keys(Keys.RETURN)
		time.sleep(self.PAUSE_TIME)

		password_input = self.driver.find_elements(By.XPATH, "//*[@autocomplete='current-password']")[0]
		password_input.send_keys(user_info["password"])
		password_input.send_keys(Keys.RETURN)
		time.sleep(self.PAUSE_TIME)

	def parse_tweet(self, tweet_url, save=True):
		self.driver.get(tweet_url)
		WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'article')))
		time.sleep(self.PAUSE_TIME)

		infos = []
		last_height = self.driver.execute_script("return document.body.scrollHeight")
		while True:
			infos += self.get_tweet()
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

			more_reply = self.driver.find_elements(By.XPATH, "//*[contains(text(), '顯示更多回覆')]")
			if more_reply:
				more_reply[0].click()
			time.sleep(self.PAUSE_TIME)
			
			new_height = self.driver.execute_script("return document.body.scrollHeight")
			if new_height == last_height:
				break
			last_height = new_height

		return infos


	def get_tweet(self):

		info = []
		for elem in self.driver.find_elements(By.XPATH, "//*[@data-testid='tweet']"):
			user = elem.find_elements(By.XPATH, ".//*[@data-testid='User-Name']")
			user = user[0].text.split('\n') if len(user) else None

			date = elem.find_elements(By.XPATH, ".//*[time]/*")
			date = date[0].get_attribute('datetime') if len(date) else None
			
			text = elem.find_elements(By.XPATH, ".//*[@data-testid='tweetText']")
			text = text[0] if len(text) else None
			content = text.find_elements(By.XPATH, ".//*")
			content = ''.join([t.get_attribute('alt') if t.tag_name == 'img' else t.text for t in content]) if len(content) else None
			
			info.append({'name': user[0], 'account': user[1], 'date': date, 'content': content})
		
		with open("info.json", "w", encoding="utf-8") as f:
			json.dump(info, f)
		
		return 

if __name__ == "__main__":

	crawler = TwitterCrawler()
	crawler.login()
	crawler.parse_tweet("https://x.com/warhound_yin/status/1743210738343383401?s=46&t=eJ927GR7M0k-wGZVswk43w")
	crawler.quit()