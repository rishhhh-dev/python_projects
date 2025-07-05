import requests
import html5lib
import psycopg2
import csv
import json
from datetime import datetime
from bs4 import BeautifulSoup
from collections import defaultdict

class BookScraper:
    def __init__(self):
       self.scraped_records = []
       self.date = datetime.now().date()
    
    def get_review_based(self,prefered_rating):
        review_books = defaultdict(list)

        for book in self.scraped_records:
            review = book['review']
            review_books[review].append(book)
        
        result = dict(sorted(review_books.items(),key=lambda x:x[0]))
        
        if prefered_rating in result.keys():
            print(result[prefered_rating])
        else:
            print("Enter prefered rating between 1-5")
    
    def scrape_data(self,url):
        try:
            send_request = requests.get(url)
            print(send_request)
            if send_request.status_code==200:
                self.web_content = send_request.content
                self.scraped_records = self.clean_data(self.web_content)
        except requests.exceptions.RequestException or requests.exceptions.ConnectionError or requests.exceptions.Timeout as e:
            print("Exception happened",e)
    
    @staticmethod
    def clean_data(web_content):
        soup = BeautifulSoup(web_content,'html5lib')

        records = []
        reviews = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5} #Converts text to number

        ordered_list = soup.find('ol',attrs={'class':'row'})
        
        for row in ordered_list.find_all('li',attrs={"class":"col-xs-6 col-sm-4 col-md-3 col-lg-3"}):
            for data in row.find_all('article',attrs={"class":"product_pod"}):
                object = {}

                object['title'] =  data.h3.find_next().attrs['title'] # <a> tag is inside <h3> tag so find_next will call <a> tag and title attribut from <a>
                
                review = data.p.extract().attrs['class'][1] #To extract class name,  class name is in array and index 1 stores review value
                review = reviews[review] #Convert str review to int review.

                object['review'] = review 
                price = data.div.find_next(attrs={'class':'product_price'}) #<p> tag is inside <div class="product_price"> tag so find_next to extract <p> text
                object['price'] = float(f"{price.p.text}".split("£")[1]) #extracting the decimal valye after £ sign and converting it into float().

                records.append(object) #Append each object/row to list 

        return records
    
    def load_data(self,host,port,user,password,db):
        try:
            db_conn = psycopg2.connect(host=host,port=port,user=user,password=password,database=db)
            cursor = db_conn.cursor()

            for row in self.scraped_records:
                title = row['title']
                
                review = row['review']
                price = row['price']

                query = """INSERT INTO books VALUES (%s,%s,%s)"""
            
                cursor.execute(query,(title,review,price))
            
            db_conn.commit()
            db_conn.close()

            print("Records added to table")

        except psycopg2.errors.DatabaseError or psycopg2.errors as e:
            print("Database Exception occurred",e)
    
    def load_data_csv(self):
        
        with open(f'Books-[{self.date}].csv','w',newline='') as f:
            try:
                fieldnames=["title","review","price"]
                writer = csv.DictWriter(f,fieldnames=fieldnames) 

                writer.writeheader()
                for record in self.scraped_records:
                    writer.writerow(record)

                print("CSV file created")

            except csv.Error or ValueError or TypeError as e:
                print("Exception Occured from CSV",e)

    def load_data_json(self):

        with open(f'Books-[{self.date}].json','w') as f:
            try:
                data= self.scraped_records
                json.dump(data,f,indent=4)
                print("JSON file created")
            except Exception as e:
                print("JSON Exception occurred",e)
        
def main():
    url = "https://books.toscrape.com/"
    book = BookScraper()
    book.scrape_data(url=url)
    book.load_data("<your_db_host>",5432,'<your_db_user>','<your_db_password>','<your_db_name>')
    book.get_review_based(1)
    book.get_review_based(6)
    book.load_data_csv()
    book.load_data_json()


if __name__ == "__main__":
    main()