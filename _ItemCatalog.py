from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from datetime import datetime
from sqlalchemy import create_engine, text, bindparam, types
from sqlalchemy.orm import sessionmaker
from _CreateDatabase import AppUser, Category, CategoryItem
# Added imports for OAuth
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

database_file = 'postgresql://postgres:postgres@localhost/ItemCatalog'


app = Flask(__name__)

# Added for OAuth
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog App"

db = create_engine(database_file)
Session = sessionmaker(db)
session = Session()


# Added for OAuth
# Create anti-forgery state token
@app.route('/login')
def showLogin():
    """Redirect to login page"""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # access_token = request.data
    access_token = request.get_data(as_text=True)

    # print("access token received %s " % access_token)

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']

    # print("app_id %s " % app_id)

    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    # print("app_secret %s " % app_secret)

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # print(result)

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
    Due to the formatting for the result from the server token exchange we
    have to split the token first on commas and select the first index which
    gives us the key : value for the server access token then we split it on
    colons to pull out the actual token value and replace the remaining quotes
    with nothing so that it can be used directly in the graph api calls
    '''
    tdata = json.loads(result)
    token = tdata['access_token']
    # print("token %s " % token)

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email,first_name,last_name' % token

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print("url sent for API access:%s" % url)
    print("API JSON result: %s" % result)
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['firstname'] = data['first_name']
    login_session['lastname'] = data['last_name']
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    # flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Get user's information for login"""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print(data)

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['firstname'] = data['given_name']
    login_session['lastname'] = data['family_name']
    login_session['email'] = data['email']
    login_session['picture'] = data['picture']

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    # flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/signout/')
def signout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['firstname']
        del login_session['lastname']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        login_session.clear()
        flash("You have successfully been logged out.")
        return redirect(url_for('showHomePage'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showHomePage'))


# User Helper Functions
def createUser(login_session):
    newUser = AppUser(userid=None,
                      firstname=login_session['firstname'],
                      lastname=login_session['lastname'],
                      email=login_session['email'])

    appUser = session.query(AppUser).filter_by(email=login_session['email']).one_or_none()
    if appUser is None:
        session.add(newUser)
        session.commit()
        return newUser.userid
    else:
        return appUser.userid


def getUserInfo(user_id):
    appUser = session.query(AppUser).filter_by(userid=user_id).one()
    return appUser


def getUserID(email):
    try:
        appUser = session.query(AppUser).filter_by(email=email).one()
        return appUser.userid
    except:
        return None


# ===== Category Functions =====

# Create a new Category
@app.route('/category/new/', methods=['GET', 'POST'])
def addCategory():
    if 'username' not in login_session:
        IsLoggedIn = False
        CurrentUser = None
    else:
        IsLoggedIn = True
        CurrentUser = login_session['user_id']

    if request.method == 'POST':
        newCategory = Category(categoryid=None,
                               categoryname=request.form['categoryname'],
                               description=request.form['description'],
                               dateadded=datetime.now(),
                               userid=request.form['userid'])
        flash('New Category %s Successfully Created' % newCategory.categoryname)
        session.add(newCategory)
        session.commit()
        return redirect(url_for('showHomePage'))
    else:
        return render_template('addCategory.html',
                               IsLoggedIn=IsLoggedIn,
                               CurrentUser=CurrentUser)


# Edit a Category
@app.route('/category/<int:categoryid>/mode/<string:mode>/',
           methods=['GET', 'POST'])
def editCategory(categoryid, mode):
    editedCategory = session.query(
        Category).filter_by(categoryid=categoryid).one()

    addedBy = session.query(AppUser).filter_by(userid=editedCategory.userid).one()
    addedbyUser = addedBy.lastname + ", " + addedBy.firstname
    fmtDateAdded = datetime.strftime(editedCategory.dateadded, '%m/%d/%y %H:%M:%S')

    if 'username' not in login_session:
        IsLoggedIn = False
        CurrentUser = None
    else:
        IsLoggedIn = True
        CurrentUser = login_session['user_id']

    if request.method == 'POST':
        if request.form['categoryname']:
            # get itemid from hidden value of form
            categoryid = request.form['categoryid']
            # query the record we need to update
            editedCategory = session.query(Category).filter_by(categoryid=categoryid).one()
            # populate remaining fields
            editedCategory.categoryname = request.form['categoryname']
            editedCategory.description = request.form['description']
            editedCategory.userid = request.form['userid']
            # save record in database
            session.commit()
            flash('Category Successfully Edited %s' % editedCategory.categoryname)
            return redirect(url_for('showCategory', categoryid=request.form['categoryid']))
    else:
        return render_template('editCategory.html', category=editedCategory,
                               addedby=addedbyUser,
                               fmtDateAdded=fmtDateAdded,
                               IsLoggedIn=IsLoggedIn,
                               CurrentUser=CurrentUser, mode=mode)


# Confirm deletion of a category
# a seperate delete function is used to delete either
# category or item based on a 'deleteType parameter
@app.route('/confirmDelCategory/<categoryid>/<deletionType>/')
def confirmDelCategory(categoryid, deletionType):
    categoryToDelete = session.query(Category).filter_by(categoryid=categoryid).one()
    return render_template('confirmDelCategory.html',
                           category=categoryToDelete,
                           deletionType=deletionType)


# ===== Category Item Functions =====

# Create a new category item
@app.route('/category/<int:categoryid>/item/new/', methods=['GET', 'POST'])
def addItem(categoryid):
    if 'username' not in login_session:
        IsLoggedIn = False
        CurrentUser = None
    else:
        IsLoggedIn = True
        CurrentUser = login_session['user_id']

    category = session.query(Category).filter_by(categoryid=categoryid).one()

    if request.method == 'POST':
            newItem = CategoryItem(itemid=None,
                                   itemname=request.form['itemname'],
                                   description=request.form['description'],
                                   dateadded=datetime.now(),
                                   categoryid=request.form['categoryid'],
                                   userid=CurrentUser)
            session.add(newItem)
            session.commit()
            flash('New Item %s Successfully Created' % (newItem.itemname))
            return redirect(url_for('showCategory',
                            categoryid=categoryid,
                            IsLoggedIn=IsLoggedIn,
                            CurrentUser=CurrentUser))
    else:
        return render_template('addItem.html',
                               categoryid=categoryid,
                               IsLoggedIn=IsLoggedIn,
                               categoryname=category.categoryname,
                               CurrentUser=CurrentUser)


# Edit a category item
@app.route('/category/<int:categoryid>/item/<int:itemid>/mode/<string:mode>/', methods=['GET', 'POST'])
def editItem(categoryid, itemid, mode):
    if 'username' not in login_session:
        IsLoggedIn = False
        CurrentUser = None
    else:
        IsLoggedIn = True
        CurrentUser = login_session['user_id']

    editedItem = session.query(CategoryItem).filter_by(itemid=itemid).one()
    category = session.query(Category).filter_by(categoryid=categoryid).one()
    addedBy = session.query(AppUser).filter_by(userid=editedItem.userid).one()
    addedbyUser = addedBy.lastname + ", " + addedBy.firstname
    fmtDateAdded = datetime.strftime(editedItem.dateadded, '%m/%d/%y %H:%M:%S')

    if request.method == 'POST':
        # get itemid from hidden value of form
        itemid = request.form['itemid']
        # query the record we need to update
        editedItem = session.query(CategoryItem).filter_by(itemid=itemid).one()
        # populate remaining fields
        editedItem.itemname = request.form['itemname']
        editedItem.description = request.form['description']
        editedItem.dateadded = request.form['dateadded']
        editedItem.categoryid = request.form['categoryid']
        editedItem.userid = request.form['userid']
        # save record in database
        session.commit()
        # redirect back to the starting page
        flash('Category Item Successfully Edited')
        return redirect(url_for('showCategory',
                        categoryid=request.form['categoryid']))
    else:
        return render_template('editItem.html', categoryid=categoryid,
                               IsLoggedIn=IsLoggedIn, CurrentUser=CurrentUser,
                               itemid=itemid, category=category,
                               fmtDateAdded=fmtDateAdded,
                               item=editedItem, addedby=addedbyUser, mode=mode)


# Confirm deletion of a category
# a seperate delete function is used to delete either
# category or item based on a 'deleteType parameter
@app.route('/confirmDelCategory/<categoryid>/item/<int:itemid>/<deletionType>/')
def confirmDelItem(categoryid, itemid, deletionType):
    if 'username' not in login_session:
        IsLoggedIn = False
        CurrentUser = None
    else:
        IsLoggedIn = True
        CurrentUser = login_session['user_id']

    itemToDelete = session.query(CategoryItem).filter_by(itemid=itemid).one()
    return render_template('confirmDelItem.html',
                           item=itemToDelete,
                           deletionType=deletionType)


# Delete a item or a category after confirmation, this is called from a POST from confirm delete
@app.route('/deleteItem/', methods=['GET', 'POST'])
def deleteItem():
    if request.method == 'POST':
        deletionType = request.form['deletionType']
        # determine what type of record we are deleting and then...
        # get itemid or category from hidden value of form
        if deletionType == 'Item':
            itemid = request.form['itemid']
            categoryid = request.form['categoryid']
            itemToDelete = session.query(CategoryItem).filter_by(itemid=itemid).one()
            session.delete(itemToDelete)
            session.commit()
            flash('%s Successfully Deleted' % itemToDelete.itemname)
            return redirect(url_for('showCategory',
                            categoryid=request.form['categoryid']))
        else:
            categoryid = request.form['categoryid']
            print("categoryid: %s" % categoryid)
            # delete all of the categories child items
            rows_deleted = session.query(CategoryItem).filter(CategoryItem.categoryid == categoryid).delete()
            # now delete the category
            categoryToDelete = session.query(Category).filter_by(categoryid=categoryid).one()
            session.delete(categoryToDelete)
            session.commit()
            flash('%s Successfully Deleted' % categoryToDelete.categoryname)

            return redirect(url_for('showHomePage'))


# Show all categories
@app.route('/')
@app.route('/homepage/')
def showHomePage():

    if 'username' not in login_session:
        IsLoggedIn = False
        CurrentUser = None
    else:
        IsLoggedIn = True
        CurrentUser = login_session['user_id']

    categories = session.query(Category).all()
    # return "This page will show all categories"

    qry = """SELECT itemname, categoryname
            FROM categoryitems INNER JOIN category on
            categoryitems.categoryid = category.categoryid
            ORDER BY categoryitems.dateadded DESC"""

    with db.connect() as con:
        recentitems = con.execute(qry)

    return render_template('homepage.html', categories=categories,
                           recentitems=recentitems,
                           IsLoggedIn=IsLoggedIn,
                           CurrentUser=CurrentUser)


@app.route('/showCategory/<int:categoryid>')
def showCategory(categoryid):

    categories = session.query(Category).all()
    tmpCategory = session.query(Category).filter_by(categoryid=categoryid).one()
    categoryname = tmpCategory.categoryname
    categoryaddedBy = tmpCategory.userid
    # return "This page will show all categories"

    if 'username' not in login_session:
        IsLoggedIn = False
        CurrentUser = None
    else:
        IsLoggedIn = True
        CurrentUser = login_session['user_id']

    qry = text("""SELECT itemid, itemname, description, dateadded, categoryid, userid
            FROM categoryitems
            Where categoryid = :x
            ORDER BY categoryitems.dateadded DESC""")

    qry = qry.bindparams(bindparam("x", type_=types.INTEGER))
    with db.connect() as con:
        categoryItems = con.execute(qry, x=categoryid).fetchall()

    return render_template('showCategory.html', categories=categories,
                           categoryid=categoryid,
                           categoryname=categoryname,
                           categoryaddedBy=categoryaddedBy,
                           categoryItems=categoryItems,
                           IsLoggedIn=IsLoggedIn,
                           CurrentUser=CurrentUser)


# === JSONs ===

# Category on CategoryItems Table JSON
@app.route('/category/<int:categoryid>/categoryitem/JSON')
def categoryCategoryitemJSON(categoryid):
    category = session.query(Category).filter_by(categoryid=categoryid).one()
    items = session.query(CategoryItem).filter_by(
        categoryid=category.categoryid).all()
    return jsonify(CategoryItem=[i.serialize for i in items])


# Category on CategoryItems Table JSON
@app.route('/item/<int:itemid>/JSON')
def CategoryitemJSON(itemid):
    categoryitem = session.query(CategoryItem).filter_by(itemid=itemid).one()
    return jsonify(CategoryItem=categoryitem.serialize)


# User Table JSON
@app.route('/users/JSON/')
def userJSON():
    users = session.query(AppUser).all()
    return jsonify(users=[r.serialize for r in users])


# Category Table JSON
@app.route('/category/JSON/')
def categoryJSON():
    categories = session.query(Category).all()
    return jsonify(users=[r.serialize for r in categories])


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super secret key4'
    app.run(host='localhost', port=5000)
    login_session.clear()
