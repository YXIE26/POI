from flask import Flask, request,  jsonify, render_template, url_for
app = Flask(__name__)
@app.route('/place')
def main():
    return render_template("index.html")

class Node:
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.next = None

class POI:
    def __init__(self, name, country, city, poi_type, votes = 0):
        self.name = name
        self.country = country
        self.city = city
        self.poi_type = poi_type
        self.votes = votes  # Initial number of votes
        self.comments = []  # Store comments

    def add_vote(self, comment=None):
        """Increments the vote count for the POI and adds a comment."""
        self.votes += 1
        if comment:
            self.comments.append(comment)

    def get_latest_comment(self):
        """Returns the most recent comment if available."""
        if self.comments:
            return self.comments[-1]
        return "No comments yet."

    def display_info(self):
        """Displays full information of the POI."""
        return f"Name: {self.name}, Country: {self.country}, City: {self.city}, Type: {self.poi_type}, Votes: {self.votes}"


class POINode:
    def __init__(self, key, data):
        self.key = key
        self.data = data
        self.next = None

class POIHashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [None] * self.size

    def hash_function(self, key):
        return hash(key) % self.size

    def insert(self, poi):
        index = self.hash_function(poi.name)
        new_node = POINode(poi.name, poi)
        if self.table[index] is None:
            self.table[index] = new_node
        else:
            current = self.table[index]
            while current.next:
                current = current.next
            current.next = new_node
poi_hash_table = POIHashTable()

class Vote:
    def __init__(self, poi, user_name, comment=None):
        self.poi = poi
        self.user_name = user_name
        self.comment = comment

class User:
    def __init__(self, user_name):
        self.user_name = user_name
        self.votes = []  # List to store user's votes (Vote objects)

    def vote_on_poi(self, poi, comment):
        """Allows a user to vote on a POI and leave a comment."""
        vote = Vote(poi, self.user_name, comment)
        self.votes.append(vote)

    def get_votes(self):
        """Returns a list of Vote objects representing the user's votes."""
        return self.votes

class UserHashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [None] * self.size

    def hash_function(self, key):
        return hash(key) % self.size

    def insert(self, user_id, user_name):
        index = self.hash_function(user_id)
        new_node = Node(user_id, User(user_name))
        if self.table[index] is None:
            self.table[index] = new_node
        else:
            current = self.table[index]
            while current.next:
                current = current.next
            current.next = new_node

    def find_user(self, user_id):
        index = self.hash_function(user_id)
        current = self.table[index]
        while current:
            if current.key == user_id:
                return current.data
            current = current.next
        return None

    def add_vote_to_user(self, user_id, poi, comment):
        user = self.find_user(user_id)
        if not user:
        # Create a new user if the user ID does not exist
          self.insert(user_id, f"User{user_id}")
          user = self.find_user(user_id)

        user.vote_on_poi(poi, comment)
        return user.get_votes()
user_hash_table = UserHashTable()


@app.route('place/fromForm', methods=['POST'])
def from_form():
    # Get the form data
    country = request.form.get('country')
    city = request.form.get('city')
    type = request.form.get('type')
    place = request.form.get('place')

    # Create a new POI and insert it into the hash table
    poi = POI(place, country, city, type)
    poi_hash_table.insert(poi)

    # Return a JSON response
    return jsonify(message="POI added successfully!")

@app.route('/filter/pois', methods=['GET'])
def get_pois():
    pois = {}
    for i in range(poi_hash_table.size):
        current = poi_hash_table.table[i]
        while current:
            poi = current.data
            if poi.country not in pois:
                pois[poi.country] = []
            if poi.city not in pois[poi.country]:
                pois[poi.country].append(poi.city)
            current = current.next
    return jsonify(pois)


@app.route('/filter', methods=['GET', 'POST'])
def filter():
    if request.method == 'POST':
        # Get the form data
        country = request.form.get('country')
        city = request.form.get('city')
        poi_type = request.form.get('type')

        # Filter the POIHashTable based on the form data
        filtered_pois = []
        for i in range(poi_hash_table.size):
            current = poi_hash_table.table[i]
            while current:
                poi = current.data
                if (not country or poi.country == country) and (not city or poi.city == city) and (not poi_type or poi.poi_type == poi_type):
                    filtered_pois.append(poi.display_info())
                current = current.next

        # Return the filtered results as a JSON response
        return jsonify(filtered_pois)
    else:
        return render_template("filter.html")

@app.route('/vote', methods=['POST'])
def vote():
    # Get the form data
    user_id = request.form.get('userId')
    poi_name = request.form.get('poiName')
    comment = request.form.get('comment')

    # Find the POI and user
    poi = poi_hash_table.find_poi(poi_name)
    user = user_hash_table.find_user(user_id)

    # Add the vote to the user and POI
    user.vote_on_poi(poi, comment)

    # Return a JSON response
    return jsonify(message="Vote added successfully!")


if __name__ == "__main__":
    app.run(debug=True)