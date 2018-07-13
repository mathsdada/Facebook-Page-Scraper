Facebook Page Post Scraper:
A tool for gathering all the posts and comments of a page and related data including post messages, counts of each reaction on the post, comment replies, user's network etc.
All this data is exported as a EXCEL document.

What is Needed:
	Python.3.6
	List of pip packages needed:
		BeautifulSoup4
		openpyxl
		pandas
		selenium
	chromedriver (save the location of this file)

List of files:
	FacebookRenderEngine.py:
		This files takes care of rendering a page and return html_source of that particular page.
	FacebookScraper.py
		This files takes care of scraping the html_source from render engine.
	Controller:
		This is the main files which takes care of excel sheet generation.
		
How to Run:
	1. In line-17 of FacebookRenderEngine.py file, add the path of chromedriver.
	2. Run the program using : python3 Controller.py
	
