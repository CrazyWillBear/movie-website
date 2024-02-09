import csv
from flask import Flask, render_template, jsonify, request
import urllib
from multiprocessing import Process, Value
import json
import os
import time

app = Flask(__name__)

# Define a route for the root URL
@app.route('/', methods=["GET", "POST"])
def index():
    reviews = load_and_sort_reviews(10)
    all_viewed = False;

    print(request.method)
    if request.method == 'POST':
        if request.form.get('view_all'):
            reviews = load_and_sort_reviews(1000)
            all_viewed = True
        elif request.form.get('view_all'):
            reviews = load_and_sort_reviews(10)
            all_viewed = False
    
    # Render an HTML template and pass the reviews to it
    return render_template('index.html', reviews=reviews, all_viewed=all_viewed)

@app.route('/review/<film_name>')
def review(film_name):
    review_data = load_review(film_name)
    if review_data:
        return render_template('review.html', review=review_data)
    else:
        return "Review not found", 404

@app.route('/about')
def about():
    return render_template('about.html')

def load_review(film_name):
    filename = "./reviews/" + film_name + ".json"
    if os.path.isfile(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    return None

def load_and_sort_reviews(stop):
    reviews = []
    directory = os.path.join(os.getcwd(), 'reviews')
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                review = json.load(f)
                reviews.append(review)
    reviews.sort(key=lambda x: x['rating'], reverse=True)
    return reviews[0:stop]  # return top `n` reviews

def add_reviews_from_csv():
    # download latest .csv sheet with reviews
    urllib.request.urlretrieve("https://docs.google.com/spreadsheets/d/e/2PACX-1vTw23TH1MEBXtnzXiEUw35wtHOzyL0VotP4RWjO8FBQ4JFR3bHfVScb0wDWvpXiQBfGp_05tzWRcZtw/pub?gid=0&single=true&output=csv", "movies.csv")
    
    # open csv file
    with open('movies.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        # go through csv file
        for row in csv_reader:
            # don't do anything to first line
            if line_count == 0:
                line_count += 1
            else:
                # add review to /reviews/<name>.json
                json_obj = {
                    "name": row[0],
                    "rating": row[1],
                    "review": row[2]
                }

                file_name = "reviews/" + (row[0].replace(' ', '-')).lower() + ".json"
                f = open(file_name, "w")
                f.write(json.dumps(json_obj, indent=4))
                f.close()
    
    # delete csv file once done
    os.remove("movies.csv")

def loop_process(delay_mins):
    while True:
        add_reviews_from_csv()
        time.sleep(60 * delay_mins)

# get the latest reviews and add to /reviews
add_reviews_from_csv()

if __name__ == '__main__':
    p = Process(target=loop_process, args=(5,))
    p.start()
    app.run(debug=False, use_reloader=False)
    p.join()
