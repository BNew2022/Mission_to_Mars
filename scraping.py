
# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # initiate the headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemishpere_images": hemispheres(browser)
    }
    browser.quit()
    return data
#executable_path = {'executable_path': ChromeDriverManager().install()}
#browser = Browser('chrome', **executable_path, headless=False)

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        #slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first 'a' tag and save it as news_title
        news_title = slide_elem.find('div', class_='content_title').get_text()
        
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p


# ### Featured Images
def featured_image(browser):
    # vist URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img',class_='fancybox-image').get('src')
        #img_url_rel
    except AttributeError:
        return None
    # USe the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url

def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    
    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes = "table table-striped")

def hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'

    browser.visit(url)
    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    # First, get a list of all of the hemispheres
    browser.is_element_present_by_css('a.product-item img', wait_time=5)
    links = browser.find_by_css('a.product-item img')
    print(len(links))
    # Next, loop through those links, click the link, find the sample anchor, return the href
    for i in range(len(links)):
        hemisphere = {}
        browser.is_element_present_by_css('a.product-item img', wait_time=5)

        # We have to find the elements on each loop to avoid a stale element exception
        browser.find_by_css('a.product-item img')[i].click()

        # Next, we find the Sample image anchor tag and extract the href
        # sample_elem = browser.links.find_by_text('Sample').first
        
        sample_elem = browser.links.find_by_text('Sample')
        hemisphere['img_url'] = sample_elem['href']

        # Get Hemisphere title
        hemisphere['title'] = browser.find_by_css('h2.title').text

        # Append hemisphere object to list
        hemisphere_image_urls.append(hemisphere)
        browser.back()
        # print(f'this is what we are looking for: {hemisphere_image_urls}')
    return hemisphere_image_urls


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())


