import http.server

import database
import json
import jwt
import user
import hashlib
import os

# Global connection
conn = database.connect_to_mysql()
cursor=conn.cursor()
cursor = conn.cursor(buffered=True)

# Global secret_key
secret_key=os.environ.get('SECRET_KEY')
# Global instance of user()
user1=user.user()

# Function responsible for hashing the password using sha256 algorithm and importing hashlib
def hash_password(password):
    """Hashes a password using the SHA-256 algorithm."""
    hash_object = hashlib.sha256()
    hash_object.update(password.encode('utf-8'))
    return hash_object.hexdigest()

# Responsible for Generation of a JWT token using PyJWT package importing jwt
# called  from loginValidate()
def GenerateToken(userName):
  payload={"user_name":userName}
  # print(secret_key)
  token=jwt.encode(payload,secret_key,algorithm="HS256")
  return token


# Responsible for checking if a user exists in the database with the specified input
# Called from login and invokes Gernerate_token() if after checking the data
def loginValidate(userName,password):
  query="SELECT pass FROM users WHERE user_name = %s"
  cursor.execute(query,(user1.userName,))
  data=cursor.fetchone()

  # if database record is empty it means no record with such info was found
  if data==None:
    print("Invalid User Name")
    return "Invalid User Name"
  # otherwise if record found, make sure the record's password equals the hashed version of given password input
  else:
    print(data)
    if password==data[0]:
      print("Welcome...")
      t=GenerateToken(userName)

      return t,"Logged-In"
    else:
      print("Wrong Password")
  return "Invalid procedure"


# Login is the handler that is called in case the url ='/login'. It parses the incoming json data from the request
# Called from def_POST() By the server which is invoked in case of a post request is made
# Calls the hash_password() function to encrypt the password before passing it along in the code
# returns the t which the is the JWT token created and also returns the status to indicate successful loging operation
def  login(data):
  json_data = json.loads(data)
  user1.userName=json_data['user_name']
  user1.password=json_data['password']
  user1.password=hash_password(user1.password)
  t,status=loginValidate(user1.userName,user1.password)
  return t,status



# Responsible for checking if a user record with this user_name already exists in the database
# true means that no record of such user is found and u can proceed with the inserting
# false means that a user already exists and user should be required to try another user_name
def validate(user1):
  t = user1
  # print(222,t)
  query="SELECT * FROM users WHERE user_name = %s"
  cursor.execute(query,(t,))
  temp=cursor.fetchone()
  # conn.commit()

  # print(temp)
  if (temp == None):
    return True
  else:
    return False

# save_data is responsible for escaping the input string
# and also responsible for inserting the data to the database
# called from get_data() and will only be invoked if valid returned true
# Print the signed-up which indicates a successful inserting operation
def save_data():
  email = user1.email.replace("'", "''").replace('"', '\\"').replace(';', '\;')
  password = user1.password.replace("'", "''").replace('"', '\\"').replace(';', '\;')
  user_name=user1.user_name.replace("'", "''").replace('"', '\\"').replace(';', '\;')
  firstName = user1.firstName.replace("'", "''").replace('"', '\\"').replace(';', '\;')
  lastName = user1.lastName.replace("'", "''").replace('"', '\\"').replace(';', '\;')
  query="INSERT INTO users (user_name,pass,first_name,last_name,email) VALUES (%s,%s,%s,%s,%s)"
  cursor.execute(query,(user_name,password,firstName,lastName,email))
  conn.commit()
  print("Signed-Up..")
  return

# binds the data from the request to the user1 which is the instance of the user class
# invokes hash_password() to has the password before moving it around
# calls valid and if true calls also save_data, If not true it requires another user_name from user
# called from register function
def get_data(j_data):
  user1.email = j_data['email']

  user1.password=j_data['password']
  user1.password=hash_password(user1.password)

  user1.user_name=j_data['user_name']
  user1.firstName=j_data['first_name']
  user1.lastName=j_data['last_name']
  # print(user1.user_name,"4444")
  valid =validate(user1.user_name)
  # print("Validation",valid)
  if valid:
    save_data()
  else:
    print("The User Name Entered is Invalid ,Please Enter another User Name ")
  return

# responsible for binding the json data into local variable
# invokes get_data()
# called only if a POST request is received by the server with the url of '/register'
def register(data):
  json_data = json.loads(data)
  # print(10)
  get_data(json_data)
  return


# Creating local server
class MyHandler(http.server.SimpleHTTPRequestHandler):
  # Managing POST requests coming to the Myhandler server and routing them based on the url
  def do_POST(self):
    url = self.path
    # reading the data in the request
    content_length = int(self.headers['Content-Length'])
    data = self.rfile.read(content_length)
    if url == '/register':
      register(data)
      temp=""
    if url== '/login':
      temp,status=login(data)
    if data:
      self.send_response(200)
      self.send_header('Content-Type', 'application/json')
      self.end_headers()
      # this is the token
      self.wfile.write(bytes(temp,'utf-8'))
      self.wfile.write(bytes("\n",'utf-8'))
      # This is the status message from login_validate()
      self.wfile.write(bytes(status,'utf-8'))
    else:
      self.send_response(404,"Can't get data")
      self.end_headers()

if __name__ == '__main__':
  # FIRING UP THE SERVER ON LOCALHOST PORT 8000
  server = http.server.HTTPServer(('localhost', 8000), MyHandler)
  server.serve_forever()
