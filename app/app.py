from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from pymongo import MongoClient
from bson import ObjectId, json_util

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# MongoDB connection details
mongo_url = "mongodb://localhost:27017/"
db_name = "task_db"
collection_name = "cred_collection"

# Function to connect to MongoDB
def connect_to_mongo():
    try:
        client = MongoClient(mongo_url)
        db = client[db_name]
        client.server_info()  # Check if server is available
        return db, client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None, None

# Function to create database and collection if not exist
def create_db_and_collection():
    db, client = connect_to_mongo()
    if db is not None:
        try:
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                print(f"Collection '{collection_name}' created successfully.")
            else:
                print(f"Collection '{collection_name}' already exists.")
        except Exception as e:
            print(f"Error creating collection: {e}")
        finally:
            if client:
                client.close()
    else:
        print("Cannot create collection. MongoDB connection failed.")

@app.route("/", methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            # Check if email already exists in the database
            db, client = connect_to_mongo()
            if db is not None:
                try:
                    collection = db[collection_name]
                    existing_document = collection.find_one({'email': email})
                    if existing_document:
                        flash("Email already exists. Please use a different email address.", "error")
                        return redirect(request.url)  # Redirect to the same page to display the flashed message
                    else:
                        # Insert new document into the collection
                        collection.insert_one({'email': email, 'password': password})
                        return redirect(url_for('collected'))  # Redirect to the collected page after successful submission
                except Exception as e:
                    print(f"Error inserting data into MongoDB: {e}")
                    flash("Error inserting data into MongoDB. Please try again later.", "error")
                    return redirect(request.url)  # Redirect to the same page to display the flashed message
                finally:
                    if client:
                        client.close()
            else:
                flash("Failed to connect to MongoDB. Please try again later.", "error")
                return redirect(request.url)  # Redirect to the same page to display the flashed message
        else:
            flash("Email and password are required.", "error")
            return redirect(request.url)  # Redirect to the same page to display the flashed message
    else:
        return render_template('index.html')

# Route to display collected data
@app.route("/collected")
def collected():
    # Here you can retrieve data from MongoDB and pass it to the collected.html template
    return render_template('collected.html')


# Route to handle viewing raw data
@app.route("/view_raw_data")
def view_raw_data():
    # Connect to MongoDB
    db, client = connect_to_mongo()
    if db is not None:
        try:
            # Retrieve data from MongoDB collection
            collection = db[collection_name]
            documents = list(collection.find())  # Retrieve all documents from the collection

            # Convert documents to JSON format using json_util
            json_data = json_util.dumps(documents)

            # Return the JSON data
            return json_data
        except Exception as e:
            print(f"Error retrieving data from MongoDB: {e}")
            return "Error retrieving data from MongoDB"
        finally:
            if client:
                client.close()
    else:
        return "Failed to connect to MongoDB"
    
from flask import request, jsonify

@app.route("/update/<string:id>", methods=['POST'])
def update_document(id):
    # Retrieve data from request body
    data = request.json
    if data:
        updated_email = data.get('email')
        updated_password = data.get('password')
        # Update document in MongoDB collection
        db, client = connect_to_mongo()
        if db is not None:
            try:
                collection = db[collection_name]
                result = collection.update_one({'_id': ObjectId(id)}, {'$set': {'email': updated_email, 'password': updated_password}})
                if result.modified_count > 0:
                    return jsonify({'message': 'Document updated successfully'}), 200
                else:
                    return jsonify({'message': 'Document not found or not modified'}), 404
            except Exception as e:
                return jsonify({'message': f'Error updating document: {e}'}), 500
            finally:
                if client:
                    client.close()
        else:
            return jsonify({'message': 'Failed to connect to MongoDB'}), 500
    else:
        return jsonify({'message': 'Invalid JSON data'}), 400



# Route to display data
@app.route("/display_data")
def display_data():
    # Connect to MongoDB
    db, client = connect_to_mongo()
    if db is not None:  # Check if the database object is not None
        try:
            # Retrieve data from MongoDB collection
            collection = db[collection_name]
            documents = list(collection.find())  # Convert cursor to list of documents
            client.close()  # Close the MongoDB client connection
            return render_template('display.html', documents=documents)
        except Exception as e:
            print(f"Error retrieving data from MongoDB: {e}")
            return "Error retrieving data from MongoDB"
    else:
        return "Failed to connect to MongoDB"

from flask import jsonify

@app.route("/delete/<string:id>", methods=['POST'])
def delete_document(id):
    # Connect to MongoDB
    db, client = connect_to_mongo()
    if db is not None:
        try:
            # Delete document from MongoDB collection
            collection = db[collection_name]
            result = collection.delete_one({'_id': ObjectId(id)})
            if result.deleted_count > 0:
                return jsonify({'message': 'Document deleted successfully'}), 200
            else:
                return jsonify({'message': 'Document not found'}), 404
        except Exception as e:
            print(f"Error deleting document from MongoDB: {e}")
            return jsonify({'message': 'Error deleting document from MongoDB'}), 500
        finally:
            if client:
                client.close()
    else:
        return jsonify({'message': 'Failed to connect to MongoDB'}), 500

    
if __name__ == "__main__":
    create_db_and_collection()  # Create database and collection if not exist
    app.run(debug=True)
