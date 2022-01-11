from flask import Flask, request, render_template, jsonify
from flask_cors import CORS, cross_origin
from urllib.request import urlopen as openlink
from bs4 import BeautifulSoup as bs
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home_page():
    return render_template(('index.html'))

@app.route('/review', methods=['POST', 'GET'])
@cross_origin()
def scrape():
    if request.method=='POST':
        try:
           searchStr = request.form['txt'].replace(' ','')
           flipkart_url = 'https://www.flipkart.com/search?q='+searchStr
           url_content = openlink(flipkart_url)
           flipkart_page = url_content.read()
           url_content.close()
           flipkart_page = bs(flipkart_page, 'html.parser')
           # print('flipkart_page------------', flipkart_page)
           boxes = flipkart_page.findAll('div', {'class':'_1AtVbE col-12-12'})
           prodlink = flipkart_url+boxes[2].div.div.div.a['href']
           # prodlink.encoding('utf-8')
           prodres = requests.get(prodlink)
           # print(prodres)
           prodres.encoding='utf-8'
           prod_page = bs(prodres.text,'html.parser')
           prod_divs = prod_page.findAll('div', {'class':'_16PBlm'})
           headers = "Product, Customer Name, Rating, Comment Heading, Comment\n"
           with open(searchStr+".csv", 'w') as fw:
               fw.write(headers)
           reviews=[]
           for prod in prod_divs:
               try:
                   name = prod.div.div.findAll('p', {'class':'_2sc7ZR _2V5EHH'})[0].text
               except Exception as e:
                   name='No Name'
               try:
                   header=prod.div.div.div.p.text
               except Exception as e:
                   header = "No header"
               try:
                   rating = prod.div.div.div.div.text
               except Exception as e:
                   rating = 0
               try:
                   comment = prod.div.div.findAll('div', {'class':''})
                   commenttag = comment[0].div.text
               except Exception as e:
                   commenttag='No Comment'

               mydict = {'Product':searchStr, 'Name':name, "Rating":rating, "CommentHead":header, "Comment":commenttag}
               reviews.append(mydict)
           # print('prod_divs-----------------',len(prod_divs))
           # rating = prod_divs[0].div.div.div.div.text
           # header = prod_divs[0].div.div.div.p.text
           # comment = prod_divs[0].div.div.findAll('div', {'class':''})
           # commenttag = comment[0].text
           # print('commenttag::', commenttag)
           # print('comment--------------',comment)
           # print('header---------------',header)
           # print('rating-----', rating)
        except Exception as e:
            print(str(e))
            return "Something is wrong"
        return render_template('results.html', reviews  = reviews[0:len(reviews)-1])
if __name__=='__main__':
    app.run()