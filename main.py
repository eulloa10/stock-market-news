from dotenv import load_dotenv
import json
import requests 
import os 
from twilio.rest import Client

load_dotenv()

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
target_date = '2021-01-15'
target_date_prior = '2021-01-14'

alpha_api_key = os.environ['ALPHA_API_KEY']
news_api_key = os.environ['NEWS_API_KEY']

stock_params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK_NAME,
    'apikey': alpha_api_key
}

stock_data = requests.get(STOCK_ENDPOINT, stock_params).json()

target_date_closing = ()
target_date_prior_closing = ()

for (date, closing_price) in stock_data['Time Series (Daily)'].items():
    if date == target_date:
        target_date_closing = (date, float(closing_price['4. close']) )
    elif date == target_date_prior:
        target_date_prior_closing = (date, float(closing_price['4. close']) )
      
price_delta = target_date_closing[1] - target_date_prior_closing[1]
arrow = None
if price_delta > 0:
    arrow = "🔺"
else:
    arrow = "🔻"

percentage_delta = round((price_delta / target_date_prior_closing[1])*100)

if abs(percentage_delta) > 1:

    news_params = {
        # 'qInTitle': COMPANY_NAME,
        'q': COMPANY_NAME,
        'sortBy': 'publishedAt',
        "from_param" : target_date,
        "to": target_date_prior,
        'apiKey': news_api_key
    }
    
    news_response = requests.get(NEWS_ENDPOINT, news_params).json()
    first_three_articles = news_response['articles'][:3]

formatted_articles = [f"{STOCK_NAME}: {arrow}{percentage_delta}%\nHeadline: {article['title']}. \nBrief: {article['description']} \nLink: {article['url']}" for article in first_three_articles]

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER']
target_phone_number =  os.environ['TARGET_PHONE_NUMBER']

client = Client(account_sid, auth_token)

for news_article in formatted_articles:
    message = client.messages \
                .create(
                     body=news_article,
                     from_=twilio_phone_number,
                     to=target_phone_number
                 )



