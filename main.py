import datetime
import os
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, request, session, redirect
import pymongo

from bson import ObjectId


myClient = pymongo.MongoClient('mongodb://localhost:27017/')
mydb = myClient["CanteenFoodOrdering"]

app = Flask(__name__)
app.secret_key = "edvarrwrvsdvrge"

food_category_col = mydb["FoodCategory"]
user_col = mydb["User"]
food_order_col = mydb["FoodOrder"]
foo_item_col = mydb["FoodItems"]
food_order_item_col = mydb["FoodOrderItem"]
deliver_boy_col = mydb["DeliveryBoy"]
review_col = mydb["Review"]
meal_plan_col = mydb["MealPlan"]
enrolled_meal_plan_col = mydb["EnrolledMealPlans"]




APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = APP_ROOT + "/static"


@app.route("/")
def home():
    food_item_name = request.args.get("food_item_name")
    FoodCategory_id = request.args.get("FoodCategory_id")
    query = {}
    if FoodCategory_id is None and food_item_name is None or FoodCategory_id == 'all' and food_item_name == 'all':
        query = {}
    elif FoodCategory_id == 'all' and food_item_name != 'all':
        rgx = re.compile(".*" + food_item_name + ".*", re.IGNORECASE)
        query = {"food_item_name": rgx}
    elif FoodCategory_id != 'all' and food_item_name == 'all':
        query = {"FoodCategory_id": ObjectId(FoodCategory_id)}
    elif FoodCategory_id != 'all' and food_item_name != 'all':
        rgx = re.compile(".*" + food_item_name + ".*", re.IGNORECASE)
        query = {"food_item_name": rgx, "FoodCategory_id": ObjectId(FoodCategory_id)}
    food_items = foo_item_col.find(query)
    categories = food_category_col.find()
    return render_template("home.html",food_items=food_items,categories=categories,getReviewCustomer=getReviewCustomer,str=str,FoodCategory_id=FoodCategory_id,getCategoryFood=getCategoryFood)

@app.route("/aLogin")
def aLogin():
    return render_template("aLogin.html")


@app.route("/uLogin")
def uLogin():
    return render_template("uLogin.html")


@app.route("/userReg")
def userReg():
    return render_template("userReg.html")

@app.route("/customerReg1",methods=['post'])
def customerReg1():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    query = {"$or":[{"email":email},{"phone":phone}]}
    count = user_col.count_documents(query)
    if count >0:
        return render_template("message.html",msg='Duplicate Details',color='text-danger')
    user_col.insert_one({"name":name,"email":email,"phone":phone,"password":password})
    return render_template("message.html", msg='User Registered Successfully', color='text-success')




@app.route("/uLogin1", methods=['post'])
def uLogin1():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = user_col.count_documents(query)
    if count > 0:
        results = user_col.find(query)
        for result in results:
            session['User_id'] = str(result['_id'])
            session['role'] = 'User'
            return redirect("/viewFood")
    else:
        return render_template("message.html", msg='Invalid Login Details', color='text-danger')

@app.route("/dLogin1", methods=['post'])
def dLogin1():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = deliver_boy_col.count_documents(query)
    if count > 0:
        results = deliver_boy_col.find(query)
        for result in results:
            session['Deliver_boy_id'] = str(result['_id'])
            session['role'] = 'Deliver_boy'
            return render_template("DeliverBoy.html")
    else:
        return render_template("message.html", msg='Invalid Login Details', color='text-danger')


@app.route("/DeliverBoy")
def DeliverBoy():
    return render_template("DeliverBoy.html")



@app.route("/aLogin1",methods=['post'])
def aLogin1():
    Username = request.form.get("Username")
    Password = request.form.get("Password")
    if Username == 'admin' and Password == 'admin':
        session['role'] = 'admin'
        return render_template("addCategory.html")
    else:
        return render_template("message.html", msg='Invalid Login Details', color='text-danger')

@app.route("/logout")
def logout():
    session.clear()
    return render_template("home.html")


# @app.route("/ahome")
# def ahome():
#     return render_template("ahome.html")

@app.route("/uhome")
def uhome():
    user = user_col.find_one({'_id':ObjectId(session['User_id'])})
    query = {"User_id":ObjectId(session['User_id'])}
    enroll = enrolled_meal_plan_col.find_one(query)
    return render_template("uhome.html",enroll=enroll,getMeanPlanByEnroll=getMeanPlanByEnroll,user=user)


def getMeanPlanByEnroll(Meal_plan_id):
    meal_plan = meal_plan_col.find_one({'_id':ObjectId(Meal_plan_id)})
    return meal_plan



@app.route("/addCategory")
def addCategory():
    return render_template("addCategory.html")

@app.route("/addCategory1",methods=['post'])
def addCategory1():
    food_category_name = request.form.get("food_category_name")
    query = {'$or':[{'food_category_name':food_category_name}]}
    count = food_category_col.count_documents(query)
    if count >0:
        return render_template("message.html",msg='Category Already Exists',color='text-danger')
    food_category_col.insert_one({"food_category_name":food_category_name})
    return render_template("message.html", msg='Category Added Successfully', color='text-success')

@app.route("/addFood")
def addFood():
    categories = food_category_col.find()
    return render_template("addFood.html",categories=categories)



@app.route("/addFood1",methods=['post'])
def addFood1():
    food_item_name = request.form.get("food_item_name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")
    units = request.form.get("units")
    photo = request.files.get("photo")
    path = APP_ROOT + "/Picture/" + photo.filename
    photo.save(path)
    FoodCategory_id = request.form.get("FoodCategory_id")
    food_description = request.form.get("food_description")
    foo_item_col.insert_one({"food_item_name":food_item_name,"price":price,"quantity":quantity,"units":units,"photo":photo.filename,"FoodCategory_id":ObjectId(FoodCategory_id),"food_description":food_description,"status":'Food Available'})
    return render_template("message.html", msg='Food Added Successfully', color='text-success')


@app.route("/viewFood")
def viewFood():
    food_item_name = request.args.get("food_item_name")
    FoodCategory_id = request.args.get("FoodCategory_id")
    query = {}
    if session['role'] == 'admin':
        if FoodCategory_id is None and food_item_name is None or FoodCategory_id == 'all' and food_item_name == 'all':
            query = {}
        elif FoodCategory_id == 'all' and food_item_name != 'all':
            rgx = re.compile(".*" + food_item_name + ".*", re.IGNORECASE)
            query = {"food_item_name": rgx}
        elif FoodCategory_id != 'all' and food_item_name == 'all':
            query = {"FoodCategory_id" : ObjectId(FoodCategory_id)}
        elif FoodCategory_id != 'all' and food_item_name != 'all':
            rgx = re.compile(".*" + food_item_name + ".*", re.IGNORECASE)
            query = {"food_item_name": rgx,"FoodCategory_id":ObjectId(FoodCategory_id)}
    elif session['role'] == 'User':
        if FoodCategory_id is None and food_item_name is None or FoodCategory_id == 'all' and food_item_name == 'all':
            query = {'status':'Food Available'}
        elif FoodCategory_id == 'all' and food_item_name != 'all':
            rgx = re.compile(".*" + food_item_name + ".*", re.IGNORECASE)
            query = {"food_item_name": rgx,"status":'Food Available'}
        elif FoodCategory_id != 'all' and food_item_name == 'all':
            query = {"FoodCategory_id": ObjectId(FoodCategory_id),'status':'Food Available'}
        elif FoodCategory_id != 'all' and food_item_name != 'all':
            rgx = re.compile(".*" + food_item_name + ".*", re.IGNORECASE)
            query = {"food_item_name": rgx, "FoodCategory_id": ObjectId(FoodCategory_id),'status':'Food Available'}

    food_items = foo_item_col.find(query)
    categories = food_category_col.find()
    return render_template("viewFood.html",getReviewCustomer=getReviewCustomer,food_item_name=food_item_name,food_items=food_items,FoodCategory_id=FoodCategory_id,getCategoryFood=getCategoryFood,categories=categories,str=str)


def getCategoryFood(FoodCategory_id):
    category = food_category_col.find_one({'_id':ObjectId(FoodCategory_id)})
    return category

@app.route("/disableFood")
def disableFood():
    Food_id = ObjectId(request.args.get("Food_id"))
    query = {'$set':{'status':'Disabled'}}
    result = foo_item_col.update_one({'_id':ObjectId(Food_id)},query)
    return viewFood()

@app.route("/enableFood")
def enableFood():
    Food_id = ObjectId(request.args.get("Food_id"))
    query = {'$set':{'status':'Food Available'}}
    result = foo_item_col.update_one({'_id':ObjectId(Food_id)},query)
    return viewFood()


@app.route("/addCart",methods=['post'])
def addCart():
    Food_item_id = request.form.get("Food_item_id")
    order_count = request.form.get("order_count")
    User_id = session['User_id']
    food_order_id = None
    query = {"User_id": ObjectId(User_id),  "status": 'Cart'}
    a = food_order_col.count_documents(query)
    print(a,"aa")
    if a == 0:
        query2 = {"User_id": ObjectId(User_id), "status": 'Cart',"date": datetime.datetime.now()}
        result = food_order_col.insert_one(query2)
        food_order_id = result.inserted_id
        print(food_order_id,"fff")
    else:
        food_orders = food_order_col.find_one({"User_id": ObjectId(User_id),"status":'Cart'})
        food_order_id = food_orders['_id']
        print(food_order_id,"fff2")
    query3 = {'food_order_id': ObjectId(food_order_id), "Food_item_id": ObjectId(Food_item_id)}
    count = food_order_item_col.count_documents(query3)
    print(count,"cccccccccc")
    if count > 0:
        food_order_item = food_order_item_col.find_one(query3)
        order_count = int(food_order_item['order_count']) + int(order_count)
        query4 = {'$set': {"order_count": order_count}}
        update = food_order_item_col.update_one({'food_order_id': ObjectId(food_order_id), "Food_item_id": ObjectId(Food_item_id)}, query4)
        print(update,"uu")
        return render_template("message.html", msg='Updated In Cart', color='text-info')
    else:
        query6 = {'food_order_id': ObjectId(food_order_id), "Food_item_id": ObjectId(Food_item_id), "order_count": order_count}
        print(query6,"iiiiiii")
        result2 = food_order_item_col.insert_one(query6)
        return render_template("message.html", msg='Added To Cart', color='text-success')


@app.route("/viewOrderItems")
def viewOrderItems():
    query = {}
    status = request.args.get("status")
    if session['role'] == 'User':
        if status == 'Cart':
            query = {"User_id":ObjectId(session['User_id']),"status":'Cart'}
        elif status == 'Ordered':
            query = {"$or":[{"status": 'Order Accepted'},{"status":'Ordered'},{"status": 'Preparing'}, {"status": 'Prepared'},{"status":'Assign To DeliverBoy'},{"status":'Delivered'}],"User_id":ObjectId(session['User_id'])}
        elif status == 'History':
            query = {"$or":[{"status":"Order Collected"},{"status":'Order Rejected'}],"User_id":ObjectId(session['User_id'])}
    elif session['role'] == 'admin':
        if status == 'Ordered':
            query = {"$or":[{"status": 'Order Accepted'},{"status":'Ordered'}]}
        elif status == 'Preparing':
            query = {"$or": [{"status": 'Preparing'}, {"status": 'Prepared'}]}
        elif status == 'Assign To DeliverBoy':
            query = {"status": 'Assign To DeliverBoy'}
        elif status == 'History':
            query = {"$or":[{"status":"Order Collected"},{"status":'Delivered'}]}
    elif session['role'] == 'Deliver_boy':
        if status == 'Assign To DeliverBoy':
            query = {"$or":[{"status":"Assign To DeliverBoy"}],"Deliver_boy_id":ObjectId(session['Deliver_boy_id'])}
        elif status == 'History':
            query = {"$or":[{"status":"Order Collected"},{"status":'Delivered'}],"Deliver_boy_id":ObjectId(session['Deliver_boy_id'])}
    order_items = food_order_col.find(query)
    return render_template("viewOrderItems.html",isFoodRated=isFoodRated,getDeliverBoy=getDeliverBoy,getUserByOrder=getUserByOrder,getFoodCategoryByOrderItem=getFoodCategoryByOrderItem,order_items=order_items,getFoodOrderItemByOrder=getFoodOrderItemByOrder,getFoodByOrderItem=getFoodByOrderItem,float=float)


@app.route("/viewMealPackageOrder")
def viewMealPackageOrder():
    status = request.args.get("status")
    query = {}
    if session['role'] == 'User':
        if status == 'MealPackageOrdered':
            query = {"User_id":ObjectId(session['User_id']),"status":'MealPackageOrdered'}
    elif session['role'] == 'admin':
        if status == 'MealPackageOrdered':
            query = {"status": 'MealPackageOrdered'}
    order_items = food_order_col.find(query)
    return render_template("viewMealPackageOrder.html",isFoodRated=isFoodRated,float=float,getFoodOrderItemByOrder=getFoodOrderItemByOrder,order_items=order_items,getUserByOrder=getUserByOrder,getFoodCategoryByOrderItem=getFoodCategoryByOrderItem,getFoodByOrderItem=getFoodByOrderItem)



def getFoodOrderItemByOrder(food_order_id):
    query = {'food_order_id':food_order_id}
    food_order_items = food_order_item_col.find(query)
    return food_order_items


def getFoodByOrderItem(Food_item_id):
    food = foo_item_col.find_one({'_id':ObjectId(Food_item_id)})
    return food



def getFoodCategoryByOrderItem(FoodCategory_id):
    category = food_category_col.find_one({'_id':ObjectId(FoodCategory_id)})
    return category

@app.route("/removeCart")
def removeCart():
    FoodOrderItem_id = request.args.get("FoodOrderItem_id")
    result = food_order_item_col.delete_one({'_id':ObjectId(FoodOrderItem_id)})
    return redirect("viewOrderItems?status=Cart")


def getUserByOrder(User_id):
    user = user_col.find_one({'_id':ObjectId(User_id)})
    return user

def isFoodRated(Food_item_id):
    query = {'Food_item_id':ObjectId(Food_item_id),"User_id":ObjectId(session['User_id'])}
    count = review_col.count_documents(query)
    return count



@app.route("/order",methods=['post'])
def order():
    order_type = request.form.get("order_type")
    totalPrice = request.form.get("totalPrice")
    FoodOrder_id = ObjectId(request.form.get("FoodOrder_id"))
    if order_type == 'OneTimeOrder':
        return render_template("order.html",FoodOrder_id=FoodOrder_id,totalPrice=totalPrice,order_type=order_type)
    else:
        return render_template("mealPackageOrder.html",FoodOrder_id=FoodOrder_id,totalPrice=totalPrice,order_type=order_type)


@app.route("/mealPackageOrder1",methods=['post'])
def mealPackageOrder1():
    from_date = request.form.get("from_date")
    to_date = request.form.get("to_date")
    order_type = request.form.get("order_type")
    totalPrice = request.form.get("totalPrice")
    FoodOrder_id = ObjectId(request.form.get("FoodOrder_id"))
    from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')
    print(type(from_date))
    print(type(to_date))
    difference = to_date - from_date
    days = difference.days
    print(days)
    print(totalPrice)
    totalAmount = int(days) * float(totalPrice)
    print(totalAmount)
    return render_template("PayMealPackageORder.html",order_type=order_type,days=days,totalAmount=totalAmount,from_date=from_date,to_date=to_date,FoodOrder_id=FoodOrder_id)


@app.route("/PayMealPackageORder1",methods=['post'])
def PayMealPackageORder1():
    FoodOrder_id = ObjectId(request.form.get("FoodOrder_id"))
    totalAmount = request.form.get("totalAmount")
    order_type = request.form.get("order_type")
    numberOfDays = request.form.get("numberOfDays")
    from_date = request.form.get("from_date")
    to_date = request.form.get("to_date")
    room_details = request.form.get("room_details")
    query = {'$set': {'status': 'MealPackageOrdered', "room_details": room_details,"order_type":order_type,"numberOfDays":numberOfDays,"from_date":from_date,"to_date":to_date,"totalAmount":totalAmount}}
    result = food_order_col.update_one({'_id': ObjectId(FoodOrder_id)}, query)
    return render_template("message.html",msg='Meal Package Ordered',color='text-success')


@app.route("/Order1",methods=['post'])
def Order1():
    order_type = request.form.get("order_type")
    FoodOrder_id = ObjectId(request.form.get("FoodOrder_id"))
    room_details = request.form.get("room_details")
    query = {'$set':{'status':'Ordered',"room_details":room_details,"order_type":order_type}}
    result = food_order_col.update_one({'_id':ObjectId(FoodOrder_id)},query)
    return redirect("viewOrderItems?status=Ordered")



@app.route("/accept")
def accept():
    FoodOrder_id = ObjectId(request.args.get("FoodOrder_id"))
    query = {'$set': {"status": 'Order Accepted'}}
    result = food_order_col.update_one({'_id': ObjectId(FoodOrder_id)}, query)
    return redirect("viewOrderItems?status=Ordered")


@app.route("/reject")
def reject():
    FoodOrder_id = ObjectId(request.args.get("FoodOrder_id"))
    query = {'$set': {"status": 'Order Rejected'}}
    result = food_order_col.update_one({'_id': ObjectId(FoodOrder_id)}, query)
    return render_template("message.html",msg='Order Rejected',color='text-danger')


@app.route("/preparing")
def preparing():
    FoodOrder_id = ObjectId(request.args.get("FoodOrder_id"))
    query = {'$set': {"status": 'Preparing'}}
    result = food_order_col.update_one({'_id': ObjectId(FoodOrder_id)}, query)
    return redirect("viewOrderItems?status=Preparing")

@app.route("/prepared")
def prepared():
    FoodOrder_id = ObjectId(request.args.get("FoodOrder_id"))
    query = {'$set': {"status": 'Prepared'}}
    result = food_order_col.update_one({'_id': ObjectId(FoodOrder_id)}, query)
    return redirect("viewOrderItems?status=Preparing")


@app.route("/assignToDeliverBoy")
def assignToDeliverBoy():
    food_order_id = ObjectId(request.args.get("food_order_id"))
    deliverboys = deliver_boy_col.find()
    return render_template("assignToDeliverBoy.html",food_order_id=food_order_id,deliverboys=deliverboys)

@app.route("/assignDeliverBoy1",methods=['post'])
def assignDeliverBoy1():
    food_order_id = ObjectId(request.form.get("food_order_id"))
    Deliver_boy_id = ObjectId(request.form.get("Deliver_boy_id"))
    query3 = {'$set':{"status":'Assign To DeliverBoy',"Deliver_boy_id":ObjectId(Deliver_boy_id)}}
    update = food_order_col.update_one({"_id":ObjectId(food_order_id)},query3)
    return redirect("viewOrderItems?status=Assign To DeliverBoy")


@app.route("/collectOrder")
def collectOrder():
    FoodOrder_id = ObjectId(request.args.get("FoodOrder_id"))
    query = {'$set':{"status":'Order Collected'}}
    result = food_order_col.update_one({'_id':ObjectId(FoodOrder_id)},query)
    return redirect("viewOrderItems?status=History")


@app.route("/dLogin")
def dLogin():
    return render_template("dLogin.html")

@app.route("/deliveryBoyReg")
def deliveryBoyReg():
    return render_template("deliveryBoyReg.html")


@app.route("/deliverBoyReg1",methods=['post'])
def deliverBoyReg1():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    query = {'$or':[{"email":email,"phone":phone}]}
    count = deliver_boy_col.count_documents(query)
    if count > 0:
        return render_template("message.html",msg='Duplicate Details',color='text-danger')
    deliver_boy_col.insert_one({'name':name,"email":email,"phone":phone,"password":password})
    return render_template("message.html", msg='Registered Successfully', color='text-success')


@app.route("/delivered")
def delivered():
    FoodOrder_id = ObjectId(request.args.get("FoodOrder_id"))
    query = {'$set':{"status":'Delivered'}}
    result = food_order_col.update_one({'_id':ObjectId(FoodOrder_id)},query)
    return redirect("viewOrderItems?status=History")


def getDeliverBoy(FoodOrder_id):
    query = {'_id':FoodOrder_id}
    food_order = food_order_col.find_one(query)
    if 'Deliver_boy_id' in food_order.keys():
        if food_order['Deliver_boy_id'] != None:
            query = {"_id": food_order['Deliver_boy_id']}
            deliverBoy = deliver_boy_col.find_one(query)
            return deliverBoy
        else:
            return None
    return None

@app.route("/rating")
def rating():
    Food_item_id = ObjectId(request.args.get("Food_item_id"))
    return render_template("rating.html",Food_item_id=Food_item_id)

@app.route("/rating1",methods=['post'])
def rating1():
    Food_item_id = ObjectId(request.form.get("Food_item_id"))
    rating = request.form.get("rating")
    review = request.form.get("review")
    review_col.insert_one({'rating':rating,"review":review,"Food_item_id":ObjectId(Food_item_id),"User_id":ObjectId(session['User_id']),"date":datetime.datetime.now()})
    return redirect("viewOrderItems?status=History")





def getReviewCustomer(Food_item_id):
    query = {"_id": Food_item_id}
    food_items = foo_item_col.find(query)
    Food_ids = []
    count = 0
    totalRating = 0
    for food_item in food_items:
        Food_ids.append({"Food_item_id": food_item['_id']})
    if len(Food_ids) == 0:
        return "No Ratings"
    query2 = {"$or": Food_ids}
    reviews = review_col.find(query2)
    if reviews != None:
        for review in reviews:
            totalRating = totalRating + int(review['rating'])
            count = count + 1
        if count > 0:
            rating = (totalRating / count)
        else:
            rating = "No Ratings"
        return rating
    else:
        return "No Ratings"

@app.route("/foodReviews")
def foodReviews():
    Food_item_id = ObjectId(request.args.get("Food_item_id"))
    query = {"_id": Food_item_id}
    food_items = foo_item_col.find(query)
    Food_ids = []
    count = 0
    totalRating = 0
    reviewsList=[]
    for food_item in food_items:
        print(food_item)
        Food_ids.append({"Food_item_id": food_item['_id']})
    if len(Food_ids) == 0:
        return "<br><br><br><h2><center>No Reviews<center></h2>"
    query2 = {"$or": Food_ids}
    reviews = review_col.find(query2)
    if reviews != None:
        for review in reviews:
            reviewsList.append(review)
        return render_template("foodReviews.html", reviewsList=reviewsList,getReviewBy=getReviewBy)
    else:
        return "<br><br><br><h2><center>No Reviews<center></h2>"


def getReviewBy(User_id):
    user = user_col.find_one({'_id':ObjectId(User_id)})
    return user


@app.route("/addMealPlan")
def addMealPlan():
    meal_plan_name = request.args.get('meal_plan_name')
    if meal_plan_name!=None:
        price = request.args.get("price")
        validity = request.args.get("validity")
        if meal_plan_name != None and price != None and validity != None:
            query = {"meal_plan_name": meal_plan_name,"price":price,"validity":validity}
            count = meal_plan_col.count_documents(query)
            if count == 0:
                meal_plan_col.insert_one(query)
            else:
                return render_template("message.html", msg="This Meal Plan already Added", color="text-danger")
    meal_plans = meal_plan_col.find()
    return render_template("addMealPlan.html",meal_plans=meal_plans)


@app.route("/addMealFood")
def addMealFood():
    Meal_plan_id = ObjectId(request.args.get("Meal_plan_id"))
    return render_template("addMealFood.html",Meal_plan_id=Meal_plan_id)


@app.route("/addMealFood1",methods=['post'])
def addMealFood1():
    Meal_plan_id = ObjectId(request.form.get("Meal_plan_id"))
    food_time = request.form.get("food_time")
    food_name = request.form.get("food_name")
    query = {'_id':ObjectId(Meal_plan_id)}
    query2 = {"$push":{ food_time:food_name}}
    print(query2)
    result = meal_plan_col.update_one(query,query2)
    return redirect('/addMealPlan')


@app.route("/enrollMealFood")
def enrollMealFood():
    validity = request.args.get("validity")
    TotalPrice = request.args.get("TotalPrice")
    Meal_plan_id = ObjectId(request.args.get("Meal_plan_id"))
    return render_template("enrollMealFood.html",Meal_plan_id=Meal_plan_id,TotalPrice=TotalPrice,validity=validity)


@app.route("/enrollMealPlan1",methods=['post'])
def enrollMealPlan1():
    validity = request.form.get("validity")
    print(validity)
    Meal_plan_id = ObjectId(request.form.get("Meal_plan_id"))
    User_id = session['User_id']
    query = {"User_id":ObjectId(User_id),"Meal_plan_id":ObjectId(Meal_plan_id)}
    enrolled_meal_plan_col.delete_one(query)
    startDate = datetime.datetime.now()
    expire_date = startDate + relativedelta(days=int(validity))
    print(expire_date)
    enrolled_meal_plan_col.insert_one({"expire_date":expire_date,"Meal_plan_id":ObjectId(Meal_plan_id),"User_id":ObjectId(User_id),"enrolled_date":datetime.datetime.now()})
    return render_template("message.html",msg='Enrolled Successfully',color='text-success')


app.run(debug=True)