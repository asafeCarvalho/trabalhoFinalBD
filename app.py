from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

db_config = {
    'user': 'najubiss',
    'password': 'chimarrutus',
    'host': 'localhost',
    'database': 'cinema'
}

def query_db(query, params=None):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, params)
    results = cursor.fetchall()
    columns = cursor.column_names
    cursor.close()
    connection.close()
    return results, columns

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consulta1', methods=['GET'])
def consulta1():
    if 'actor_name' in request.args:
        actor_name = request.args.get('actor_name', default='', type=str)
        query = """
        SELECT movie.title AS 'Movie Name' FROM actor
        JOIN acts ON actor.id_actor = acts.id_actor
        JOIN movie ON movie.id_movie_lens = acts.id_movie_lens
        WHERE actor.name_actor LIKE %s
        ORDER BY movie.title ASC;
        """
        results, columns = query_db(query, (f"%{actor_name}%",))
        return render_template('consulta1.html', results=results, columns=columns)
    return render_template('consulta1.html')

@app.route('/consulta2', methods=['GET'])
def consulta2():
    if 'genre1' in request.args and 'genre2' in request.args and 'genre3' in request.args:
        genre1 = request.args.get('genre1', type=int)
        genre2 = request.args.get('genre2', type=int)
        genre3 = request.args.get('genre3', type=int)
        query = """
        SELECT m.title AS 'Movie Name', AVG(r.rating) AS 'Average Rating' FROM movie m
        JOIN rates r ON m.id_movie_lens = r.id_movie_lens
        WHERE m.id_movie_lens IN (
            SELECT hg1.id_movie_lens FROM has_genre hg1
            WHERE hg1.id_genre = %s
            AND hg1.id_movie_lens IN (
                SELECT hg2.id_movie_lens FROM has_genre hg2
                WHERE hg2.id_genre = %s
                AND hg2.id_movie_lens IN (
                    SELECT hg3.id_movie_lens FROM has_genre hg3
                    WHERE hg3.id_genre = %s
                )
            )
        )
        GROUP BY m.id_movie_lens
        ORDER BY AVG(r.rating) DESC, m.title ASC
        LIMIT 10;
        """
        results, columns = query_db(query, (genre1, genre2, genre3))
        return render_template('consulta2.html', results=results, columns=columns)
    return render_template('consulta2.html')

@app.route('/consulta3', methods=['GET'])
def consulta3():
    if 'prod_country' in request.args and 'spoken_lang' in request.args:
        prod_country = request.args.get('prod_country', default='', type=str)
        spoken_lang = request.args.get('spoken_lang', default='', type=str)
        query = """
        SELECT m.title AS 'Title' FROM movie m
        JOIN country_of_origin co ON m.id_movie_lens = co.id_movie_lens
        JOIN available_in_lang al ON m.id_movie_lens = al.id_movie_lens
        WHERE co.id_prod_country = %s AND al.id_spoken_lang = %s;
        """
        results, columns = query_db(query, (prod_country, spoken_lang))
        return render_template('consulta3.html', results=results, columns=columns)
    return render_template('consulta3.html')

@app.route('/consulta4', methods=['GET'])
def consulta4():
    if 'movie_title' in request.args:
        movie_title = request.args.get('movie_title', default='', type=str)
        query = """
        SELECT m.*, COUNT(r.id_user) AS 'Number of Ratings', AVG(r.rating) AS 'Average Rating' FROM movie m
        LEFT OUTER JOIN rates r ON m.id_movie_lens = r.id_movie_lens
        WHERE m.title LIKE %s
        GROUP BY m.id_movie_lens;
        """
        results, columns = query_db(query, (f"%{movie_title}%",))
        return render_template('consulta4.html', results=results, columns=columns)
    return render_template('consulta4.html')

@app.route('/consulta5', methods=['GET'])
def consulta5():
    query = """
    SELECT c.id_collection AS 'Collection ID', c.name_collection AS 'Collection Name',
           COUNT(filmes_avaliados.id_movie_lens) AS 'Number of Movies',
           AVG(IFNULL(avg_rating, 0)) AS 'Average Rating of Collection'
    FROM collection c
    JOIN (
        SELECT m.id_collection, m.id_movie_lens, AVG(r.rating) AS avg_rating
        FROM movie m
        LEFT JOIN rates r ON m.id_movie_lens = r.id_movie_lens
        GROUP BY m.id_movie_lens
    ) AS filmes_avaliados ON c.id_collection = filmes_avaliados.id_collection
    GROUP BY c.id_collection
    HAVING COUNT(filmes_avaliados.id_movie_lens) >= 2
    ORDER BY AVG(IFNULL(avg_rating, 0)) DESC, c.name_collection ASC
    LIMIT 10;
    """
    results, columns = query_db(query)
    return render_template('consulta5.html', results=results, columns=columns)

if __name__ == '__main__':
    app.run(debug=True)
