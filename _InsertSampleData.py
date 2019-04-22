from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from _CreateDatabase import AppUser, Category, CategoryItem

# project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = 'postgresql://postgres:postgres@localhost/ItemCatalog'

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
# silence the deprecation warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# insert User data
User1 = AppUser(None, 'Savion', 'Jackson', 'savion.dev@gmail.com')
User2 = AppUser(None, 'Alexander', 'Jackson', 'savionjackson72@gmail.com')
User3 = AppUser(None, 'Saybo', 'Jackson', 'savionjobs@gmail.com')
db.session.add(User1)
db.session.add(User2)
db.session.add(User3)
db.session.commit()

# Enter some categories by user 1
Category1 = Category(None, 'Dogs', 'Dog breeds', datetime.now(), User1.userid)
Category2 = Category(None, 'Cats', 'Cat breeds', datetime.now(), User1.userid)
Category3 = Category(None, 'Birds', 'Bird breeds', datetime.now(), User1.userid)
# Enter some categories by user 2
Category4 = Category(None, 'Frogs', 'Kinds of Frogs', datetime.now(), User2.userid)
Category5 = Category(None, 'Lizards', 'Kinds of Lizards', datetime.now(), User2.userid)
# Enter some categories by user 3
Category6 = Category(None, 'Horses', 'Types of Horses', datetime.now(), User3.userid)

db.session.add(Category1)
db.session.add(Category2)
db.session.add(Category3)
db.session.add(Category4)
db.session.add(Category5)
db.session.add(Category6)
# commit the changes
db.session.commit()

# Enter some items for each Category
Item1 = CategoryItem(None, 'German Shepherd', 'medium to large-sized working dog that originated in Germany', datetime.now(), Category1.categoryid, User1.userid)
Item2 = CategoryItem(None, 'Dobermann Pincher', 'medium-large breed of domestic dog that was originally developed around 1890', datetime.now(), Category1.categoryid, User1.userid)
Item3 = CategoryItem(None, 'Border Collie', 'A remarkably bright workaholic', datetime.now(), Category1.categoryid, User1.userid)
# Enter some categories by user 2
Item4 = CategoryItem(None, 'Poison Dart Frog', 'group of frogs native to tropical Central and South America', datetime.now(), Category4.categoryid, User2.userid)
Item5 = CategoryItem(None, 'African Drawf Frog', 'aquatic frogs native to parts of Equatorial Africa', datetime.now(), Category4.categoryid, User2.userid)
# Enter some categories by user 3
Item6 = CategoryItem(None, 'Mustang', 'free-roaming horse of the American west ', datetime.now(), Category6.categoryid, User3.userid)
Item7 = CategoryItem(None, 'Clydesdale', 'a breed of draft horse named for and derived from the farm horses of Clydesdale, Scotland ', datetime.now(), Category6.categoryid, User3.userid)

db.session.add(Item1)
db.session.add(Item2)
db.session.add(Item3)
db.session.add(Item4)
db.session.add(Item5)
db.session.add(Item6)
db.session.add(Item7)

# commit the changes
db.session.commit()
