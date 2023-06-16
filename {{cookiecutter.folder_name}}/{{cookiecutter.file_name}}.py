
# Import necessary libraries
from flask import Flask, jsonify
import os
import json
from pymongo import MongoClient


# Task 1: Read all the JSON files present in the folder


def read_json_files(folder_path):
    """
    read all the json files present in the folder
    """
    json_files = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.json'):
            json_files.append(os.path.join(folder_path, file_name))
    return json_files


# Task 2: Connect to MongoDB and create a database and collection
def create_database_collection(database_name, collection_name):
    """
    connect to mongodb and create a database and collection
    """
    client = MongoClient()
    db = client[database_name]
    # Trigger the creation of the database by inserting a dummy document
    # db[collection_name].insert_one({})  # execute this only if database is not created in MongoDB .
    collection = db[collection_name]
    return collection

# Delete all the existing document present in the collection


def delete_all_documents(collection):
    """
    Delete all documents in the given collection.
    """
    collection.delete_many({})

# Task 3: Insert each JSON file as a document with title and content fields


def insert_json_documents(collection, json_files):
    """
    Insert each JSON file as a document with title and content fields

    """
    
    json_files = read_json_files(folder_path)
    documents = []
    existing_titles = set(collection.distinct('Title'))
    for file_path in json_files:
        # print(file_path)
        with open(file_path, 'r') as file:
            json_content = json.load(file)
        document = {
            'Title': os.path.basename(file_path),
            'Content': json_content
        }
        # print(document)
        if document['Title'] not in existing_titles:  # Check if the title is already present
            documents.append(document)
            # Add the new title to the set
            existing_titles.add(document['Title'])
    if documents:  # Only insert if there are new documents
        # print("new document",documents)
        collection.insert_many(documents)


# Task 4
# create an Flask API which will check if new json file is added in the folder and insert the new document in mongoDB collection
# if applicable then return the list of all the titles of the JSON files present in the MongoDB collection

def create_flask_api(collection):
    """
    creating a flask api which will return field 'title' 
    of the all the json documents present in the mongodb collection for a particular Database

    """
    app = Flask(__name__)
    
    @app.route('/', methods=['GET'])
    def get_documents():
        delete_all_documents(collection)
        insert_json_documents(collection, json_files)
        # print(collection.count_documents({}))
        documents = collection.find({}, {'Title': 1, '_id': 0})
        titles = [dict(i=i, title=doc['Title']) for i, doc in enumerate(documents, start=1)]

        return jsonify(titles)

    return app


database_name = 'JsonRepo'  # provide the database name
collection_name = 'JsonFiles'  # provide the collection name
# folder_path = 'jsonFiles'  # provide the relative/ absolute folder path
folder_path = 'jsonFiles'
while not os.path.isdir(folder_path):
    print("Path does not exist. Please enter a valid path.")

# Task 1: Read all the JSON files
json_files = read_json_files(folder_path)

# Task 2: Connect to MongoDB and create a database and collection
collection = create_database_collection(database_name, collection_name)

# Task 3: Insert each JSON file as a document
# insert_json_documents(collection, json_files)

# delete_all_documents(collection) # uncomment when delete all documents inside collection for testing purpose only


app = create_flask_api(collection)



if __name__ == '__main__':
    """
        running the flask api

    """
    app.run(debug=True)
