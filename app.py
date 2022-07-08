from flask import Flask, render_template, g, request
from datetime import datetime
from database import get_db

app = Flask(__name__)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['POST', 'GET'])
def index():
    db = get_db()

    if request.method == 'POST':
        date = request.form['date']  # assume date is YYY-MM-DD format
        dt = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(dt, '%Y%m%d')

        try:
            db.execute('INSERT INTO log_date (entry_date) VALUES (?)',
                       [database_date])
            db.commit()
        except:
            pass

    cur = db.execute('SELECT log_date.entry_date, '
                     'IFNULL(sum(food.protein), 0) as protein, '
                     'IFNULL(sum(food.carbohydrates), 0) as carbohydrates, '
                     'IFNULL(sum(food.fat), 0) as fat, '
                     'IFNULL(sum(food.calories), 0) as calories '
                     'FROM log_date LEFT JOIN food_date on log_date.id=food_date.log_date_id '
                     'LEFT JOIN food on food.id=food_date.food_id '
                     'GROUP BY log_date.id ORDER BY log_date.entry_date ASC')
    dates = cur.fetchall()

    date_results = []
    for item in dates:
        single_date = {}
        d = datetime.strptime(str(item['entry_date']), '%Y%m%d')

        single_date['entry_date'] = datetime.strftime(d, '%B %d, %Y')
        single_date['data_date'] = str(item['entry_date'])
        single_date['protein'] = item['protein']
        single_date['carbohydrates'] = item['carbohydrates']
        single_date['fat'] = item['fat']
        single_date['calories'] = item['calories']

        date_results.append(single_date)

    print(date_results)

    return render_template('home.html', dates=date_results, page_name='Home')


@app.route('/view/<date>', methods=['GET', 'POST'])  # date will be in form of yyyymmdd
def view(date):
    db = get_db()

    cur = db.execute('SELECT id, entry_date from log_date where entry_date = ?', [date])
    date_result = cur.fetchone()

    if request.method == 'POST':
        try:
            db.execute("INSERT INTO food_date (food_id, log_date_id) values (?,?)",
                       [request.form['food-select'], date_result['id']])
            db.commit()
        except:
            pass
        # return '<h1>The food item added is #{}</h1>'.format(request.form['food-select'])

    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')
    # return '<h1>The date is {}</h1>'.format(pretty_date)

    food_cur = db.execute('SELECT id, name FROM food')
    food_names = food_cur.fetchall()

    log_cur = db.execute("SELECT log_date.entry_date, food.name, food.protein, "
                         "food.carbohydrates, food.fat, food.calories "
                         "FROM food_date JOIN food ON food.id=food_date.food_id "
                         "JOIN log_date ON log_date.id = food_date.log_date_id "
                         "WHERE log_date.entry_date = ?", [date])
    log_results = log_cur.fetchall()
    totals = {'protein': 0,
              'carbohydrates': 0,
              'fat': 0,
              'calories': 0
              }
    for item in log_results:
        totals['protein'] += item['protein']
        totals['carbohydrates'] += item['carbohydrates']
        totals['fat'] += item['fat']
        totals['calories'] += item['calories']
    print(totals)

    return render_template('day.html', date=pretty_date, food_names=food_names,
                           totals=totals, log_items=log_results, this_date=date,
                           page_name='View Date')


@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()

    if request.method == 'POST':
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrate = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])

        calories = protein * 4 + carbohydrate * 4 + fat * 9

        db.execute('INSERT INTO food (name, protein, carbohydrates, fat, calories) '
                   'VALUES (?, ?, ?, ?, ?)',
                   [name, protein, carbohydrate, fat, calories])
        db.commit()
        # return "<h1>Name: {}, protein: {}, carbs: {}, fat: {}, calories: {}</h1>".format(
        #     name, protein, carbohydrate, fat, calories
        # )
    cur = db.execute('SELECT name, protein, carbohydrates, fat, calories FROM food')
    results = cur.fetchall()

    return render_template('add_food.html', foods=results, page_name='Food Viewer')


if __name__ == '__main__':
    app.run(debug=True)
