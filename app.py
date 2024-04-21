from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import mysql.connector
app = Flask(__name__)

db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="dbsing"
)
    # Create a cursor object to execute queries
cursor = db_connection.cursor()

model_path = 'gaussalgo/T5-LM-Large-text2sql-spider'
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# prompt = """
# you are a bot to assist in creating MySQL commands, all your answers should start with \
# this is your MySQL, and after that MySQL that can do what the user requests. \
# Give the answer relevant to the schema only, otherwise prompt "Irrelevant query". \
# Generate the queries containing the columns strictly present in the schema, otherwise prompt "Error!". \
# Try to maintain the MySQL order simple. \
# Put the MySQL command in white letters with a black background, and just after \
# a simple and concise text explaining how it works. \
# If the user asks for something that cannot be solved with a MySQL Order, \
# just answer something nice and simple, maximum 10 words, asking him for something that \
# can be solved with MySQL.
# """
prompt = """
When receiving a request, begin the response with "This is your SQL:". Follow with an SQL command that fulfills the user's specified need, presented in white text on a black background. Directly after, offer a concise explanation of how the command works, tailored for users with basic SQL knowledge.

Ensure SQL commands accurately handle data types, especially boolean values, which should only use 'TRUE' or 'FALSE'. If a user's query is not solvable by SQL, respond politely, urging a SQL-solvable question, limited to 10 words.

Keep SQL commands simple for ease of understanding and execution. This ensures that the commands are accessible and executable by users with basic MySQL knowledge, avoiding complex syntax or advanced features unless specifically requested by the user.
"""

schema = """
CREATE TABLE stadium (
    Stadium_ID INT PRIMARY KEY,
    Location TEXT,
    Name TEXT,
    Capacity INT,
    Highest INT,
    Lowest INT,
    Average INT
);

CREATE TABLE singer (
    Singer_ID INT PRIMARY KEY,
    Name TEXT,
    Country TEXT,
    Song_Name TEXT,
    Song_release_year TEXT,
    Age INT,
    Is_male TEXT
);

CREATE TABLE concert (
    concert_ID INT PRIMARY KEY,
    concert_Name TEXT,
    Theme TEXT,
    Year TEXT,
    Stadium_ID INT,
    FOREIGN KEY (Stadium_ID) REFERENCES stadium(Stadium_ID)
);

CREATE TABLE singer_in_concert (
    concert_ID INT,
    Singer_ID INT,
    PRIMARY KEY (concert_ID, Singer_ID),
    FOREIGN KEY (concert_ID) REFERENCES concert(concert_ID),
    FOREIGN KEY (Singer_ID) REFERENCES singer(Singer_ID)
);
"""

@app.route('/')
def index():
    return render_template('index.html', prompt=prompt)

@app.route('/query', methods=['POST'])
def query():
    user_question = request.json['user_question']
    input_text = f"Question: {user_question}\n{prompt}\nSchema:{schema}"
    model_inputs = tokenizer(input_text, return_tensors="pt")
    outputs = model.generate(**model_inputs, max_length=542)
    sql_query = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
    # print(sql_query)

    # Example query
    query = sql_query

    # Execute the query with parameters
    cursor.execute(query)

    # Fetch all rows from the result
    result = cursor.fetchall()
    # Format result for display
    # formatted_result = [str(row) for row in result]

    # return jsonify({'sql_query': sql_query, 'result': formatted_result})
    return jsonify({'sql_query': sql_query, 'result':result})
    # return jsonify({'sql_query': sql_query})

if __name__ == '__main__':
    app.run(debug=True)