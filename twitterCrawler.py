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
import pickle
import re
from pathlib import Path

class twitterCrawler:

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
	
	def _read_cookie(self):
		try:
			cookies = pickle.load(open("cookies.pkl", "rb"))
			for cookie in cookies:
				self.driver.add_cookie(cookie)
			return True
		except:
			return False
	
	def _write_cookie(self):
		pickle.dump(self.driver.get_cookies() , open("cookies.pkl","wb"))

	def login(self):

		self.driver.get(self.LOGIN_PAGE)

		if self._read_cookie():
			return

		with open('.env') as f:
			user_info = json.load(f)
		
		WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, "//*[@autocomplete='username']")))

		username_input = self.driver.find_elements(By.XPATH, "//*[@autocomplete='username']")[0]
		username_input.send_keys(user_info["username"])
		username_input.send_keys(Keys.RETURN)
		time.sleep(self.PAUSE_TIME)

		password_input = self.driver.find_elements(By.XPATH, "//*[@autocomplete='current-password']")[0]
		password_input.send_keys(user_info["password"])
		password_input.send_keys(Keys.RETURN)
		time.sleep(self.PAUSE_TIME)

		self._write_cookie()

	def parseTweet(self, tweet_url, tweet_type, save_json=True):
		self.driver.get(tweet_url)
		if tweet_type == "article":
			WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'article')))
		time.sleep(self.PAUSE_TIME)

		infos = []
		last_height = self.driver.execute_script("return document.body.scrollHeight")
		while True:
			infos += self.getTweet(tweet_type)
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

			more_reply = self.driver.find_elements(By.XPATH, "//*[contains(text(), '顯示更多回覆')]")
			if more_reply:
				more_reply[0].click()
				infos += self.getTweet(tweet_type)
			time.sleep(self.PAUSE_TIME)
			
			new_height = self.driver.execute_script("return document.body.scrollHeight")
			if new_height == last_height:
				break
			last_height = new_height

		if save_json:
			with open("info.json", "w", encoding="utf-8") as f:
				json.dump(infos, f)

		return infos


	def getTweet(self, tweet_type=None):

		info = []

		if tweet_type == "article":

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
	
		elif tweet_type == "img":
			for elem in self.driver.find_elements(By.XPATH, "//img[contains(@src,'pbs.twimg.com/media')]"):
				img_link = re.search('.+jpg', elem.get_attribute("src"))
				if img_link:
					info.append(img_link.group())
		return info

if __name__ == "__main__":

	crawler = twitterCrawler()
	crawler.login()
	crawler.parseTweet("https://x.com/yotta_zzz/media", "img")
	crawler.quit()
