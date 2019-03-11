import feedparser as fp
import json
import newspaper
from newspaper import Article
from time import mktime
from datetime import datetime
import csv

# Set the limit for number of articles to download
LIMIT = 10
articles_array = []

data = {}
data['newspapers'] = {}

# Loads the JSON files with news sites
with open('NewsPapers.json') as data_file:
    companies = json.load(data_file)

count = 1
# Iterate through each new political website
for company, value in companies.items():
    if 'rss' in value:
        d = fp.parse(value['rss'])
        print("Downloading articles from ", company)
        newsPaper = {
            "rss": value['rss'],
            "link": value['link'],
            "articles": []
        }
        for entry in d.entries:
            # Check if publish date is provided, if no the article is skipped.
            # This is done to keep consistency in the data and to keep the script from crashing.
            if hasattr(entry, 'published'):
                if count > LIMIT:
                    break
                article = {}
                article['link'] = entry.link
                date = entry.published_parsed
                article['published'] = datetime.fromtimestamp(mktime(date)).isoformat()
                try:
                    content = Article(entry.link)
                    content.download()
                    content.parse()
                except Exception as e:
                    # If the download for some reason fails (ex. 404) the script will continue downloading
                    # the next article.
                    print(e)
                    print("continuing...")
                    continue
                article['title'] = content.title
                article['text'] = content.text
                article['authors'] = content.authors
                article['top_image'] = content.top_image
                newsPaper['articles'].append(article)
                articles_array.append(article)
                print(count, "articles downloaded from", company, ", url: ", entry.link)
                count = count + 1
    else:
        # This is the fallback method if a RSS-feed link is not provided.
        # It uses the python newspaper library to extract articles
        print("Building site for ", company)
        paper = newspaper.build(value['link'], memoize_articles=False)
        newsPaper = {
            "link": value['link'],
            "articles": []
        }
        noneTypeCount = 0
        for content in paper.articles:
            if count > LIMIT:
                break
            try:
                content.download()
                content.parse()
            except Exception as e:
                print(e)
                print("continuing...")
                continue
            # Again, for consistency, if there is no found publish date the article will be skipped.

            article = {}
            article['title'] = content.title
            article['authors'] = content.authors
            article['text'] = content.text
            article['top_image'] = content.top_image
            article['link'] = content.url
            article['published'] = content.publish_date
            newsPaper['articles'].append(article)
            articles_array.append(article)
            print(count, "articles downloaded from", company, " using newspaper, url: ", content.url)
            count = count + 1
            #noneTypeCount = 0
    count = 1
    data['newspapers'][company] = newsPaper

    try:
        f = csv.writer(open('Scraped_data_news_output.csv', 'w', encoding='utf-8'))
        f.writerow(['Title', 'Authors', 'Text', 'Image', 'Link', 'Published_Date'])
        # print(article)
        for artist_name in articles_array:
            title = artist_name['title']
            authors = artist_name['authors']
            text = artist_name['text']
            image = artist_name['top_image']
            link = artist_name['link']
            publish_date = artist_name['published']
            # Add each artist’s name and associated link to a row
            f.writerow([title, authors, text, image, link, publish_date])
    except Exception as e:
        print(e)

    try:
        with open('scraped_data_news_output_raw.json', 'w') as outfile:
            json.dump(data, outfile)
    except Exception as e:
        print(e)