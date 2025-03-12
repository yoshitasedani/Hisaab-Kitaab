from flask import Flask, render_template, request, jsonify, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, Item, User, Rental
from flask_cors import CORS
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DATABASE_URL = "sqlite:///accounting_software.db"
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/items")
def items_page():
    return render_template("items.html")

@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        item_id = request.form.get("item_id")
        description = request.form.get("description")
        category = request.form.get("category")
        rent = request.form.get("rent")
        quantity = request.form.get("quantity")


        existing_item = session.query(Item).filter_by(item_id=item_id).first()
        if existing_item:
            return render_template("add_item.html", error="Item ID is already used. Please choose a unique ID.")

        new_item = Item(
            item_id=item_id,
            description=description,
            category=category,
            rent=float(rent),
            quantity=int(quantity),
            availability=True,
        )
        session.add(new_item)
        session.commit()
        return redirect(url_for("items_page"))

    return render_template("add_item.html")


@app.route("/fetch_item_page")
def fetch_item_page():
    return render_template("fetch_item.html")

@app.route("/fetch_item", methods=["POST"])
def fetch_item():
    item_id = request.form.get("item_id")
    try:
        item = session.query(Item).filter_by(item_id=item_id).one()
        return render_template("modify_item.html", item=item)
    except NoResultFound:
        return render_template("fetch_item.html", error="Item not found")


@app.route("/modify_item/<string:item_id>", methods=["POST"])
def modify_item(item_id):
    try:
        item = session.query(Item).filter_by(item_id=item_id).one()
        item.description = request.form.get("description")
        item.category = request.form.get("category")
        item.rent = float(request.form.get("rent"))
        item.quantity = int(request.form.get("quantity"))

        # Commit changes to the database
        session.commit()
        return "Item updated successfully!", 200
    except NoResultFound:
        return "Item not found!", 404
    except Exception as e:
        session.rollback()
        return f"An error occurred: {str(e)}", 500


@app.route("/get_item_details")
def get_item_details():
    item_id = request.args.get("item_id")
    try:
        # Fetch the item details from the database
        item = session.query(Item).filter_by(item_id=item_id).one_or_none()
        if not item:
            return jsonify({"success": False, "error": "Item not found"}), 404

        # Return the maximum quantity available
        return jsonify({"success": True, "max_quantity": item.quantity}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/rent")
def rent_page():
    return render_template("/select_user.html")


@app.route("/search_user")
def search_user():
    query = request.args.get("query", "").lower()
    users = session.query(User).filter(User.name.ilike(f"%{query}%")).all()
    user_list = [{"name": user.name, "phone_number": user.phone_number} for user in users]
    return jsonify({"users": user_list})



@app.route("/select_user", methods=["POST"])
def select_user():
    selected_user = request.form.get("user")

    if selected_user == "add_user":
        # Redirect to Add User page if 'Add User' is selected
        return redirect("/add_user")
    else:
        # Fetch the user details to ensure the user exists
        user = session.query(User).filter_by(name=selected_user).first()
        if not user:
            return "User not found", 404

        # Redirect to the rental details page
        return redirect(f"/rental_details/{user.user_id}")


from datetime import datetime, timedelta

# @app.route("/finalize_rental", methods=["POST"])
# def finalize_rental():
#     try:
#         data = request.json
#         user_id = data["user_id"]
#         items = data["items"]

#         for item in items:
#             item_id = item["item_id"]
#             quantity = int(item["quantity"])
#             date_of_issuing = item.get("date_of_issuing")  # Pass from the form
#             number_of_days = int(item.get("number_of_days", 0))  # Get from form

#             if not date_of_issuing:
#                 return jsonify({"success": False, "error": "Date of issuing is required"}), 400

#             date_of_issuing = datetime.strptime(date_of_issuing, "%Y-%m-%d").date()
#             due_date = date_of_issuing + timedelta(days=number_of_days)

#             # Check if item exists
#             db_item = session.query(Item).filter_by(item_id=item_id).one_or_none()
#             if not db_item:
#                 return jsonify({"success": False, "error": f"Item {item_id} does not exist in database"}), 400

#             available_stock = db_item.quantity - db_item.issued_quantity

#             if available_stock < quantity:
#                 return jsonify({"success": False, "error": f"Item {item_id} has only {available_stock} available, but {quantity} requested"}), 400

#             # Update item quantities
#             db_item.issued_quantity += quantity
#             session.commit()  # Ensure change is stored before proceeding

#             # Calculate total rent
#             total_rent = db_item.rent * quantity * number_of_days

#             # Create a rental record
#             rental = Rental(
#                 user_id=user_id,
#                 item_id=item_id,
#                 date_of_booking=datetime.now().date(),
#                 date_of_issuing=date_of_issuing,
#                 due_date=due_date,
#                 number_of_days=number_of_days,  # Save the number of days
#                 quantity_issued=quantity,
#                 rent=db_item.rent,
#                 total_rent=total_rent,
#                 balance=total_rent  # Adjust as needed for advance payments
#             )
#             session.add(rental)

#         session.commit()
#         return jsonify({"success": True}), 200
#     except Exception as e:
#         session.rollback()
#         return jsonify({"success": False, "error": str(e)}), 500



# @app.route("/finalize_bill", methods=["POST"])
# def finalize_bill():
#     try:
#         advance = float(request.form.get("advance"))
#         user_id = request.form.get("user_id")  # Retrieve from form instead of session

#         if not user_id:
#             return "User ID is missing", 400

#         rentals = session.query(Rental).filter_by(user_id=user_id).all()

#         if not rentals:
#             return "No rentals found for this user", 404

#         for rental in rentals:
#             rental.advance = advance
#             rental.balance = rental.total_rent - advance

#         session.commit()

#         return redirect(url_for("bill_summary", user_id=user_id))  # Use `url_for` for safety
#     except Exception as e:
#         session.rollback()
#         return f"An error occurred: {str(e)}", 500



# @app.route("/bill_summary/<int:user_id>")
# def bill_summary(user_id):
#     try:
#         # Fetch rentals for the specific user
#         user_rentals = session.query(Rental).filter_by(user_id=user_id).all()

#         if not user_rentals:
#             return "No rentals found for this user.", 404

#         # Calculate total rent for the user
#         total_rent = sum(rental.total_rent for rental in user_rentals)

#         return render_template("billing_summary.html", rentals=user_rentals, total_rent=total_rent)
#     except Exception as e:
#         return f"An error occurred: {str(e)}", 500


@app.route("/finalize_rental", methods=["POST"])
def finalize_rental():
    try:
        data = request.json
        print("Received Data:", data)  # Debugging

        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"success": False, "error": "User ID is missing"}), 400

        items = data["items"]
        rental_ids = []  # Store rental IDs

        for item in items:
            item_id = item["item_id"]
            quantity = int(item["quantity"])
            date_of_issuing = item.get("date_of_issuing")
            number_of_days = int(item.get("number_of_days", 0))

            if not date_of_issuing:
                return jsonify({"success": False, "error": "Date of issuing is required"}), 400

            date_of_issuing = datetime.strptime(date_of_issuing, "%Y-%m-%d").date()
            due_date = date_of_issuing + timedelta(days=number_of_days)

            db_item = session.query(Item).filter_by(item_id=item_id).one_or_none()
            if not db_item:
                return jsonify({"success": False, "error": f"Item {item_id} does not exist"}), 400

            available_stock = db_item.quantity - db_item.issued_quantity
            if available_stock < quantity:
                return jsonify({"success": False, "error": f"Only {available_stock} available"}), 400

            db_item.issued_quantity += quantity
            session.commit()

            total_rent = db_item.rent * quantity * number_of_days
            rental = Rental(
                user_id=user_id,
                item_id=item_id,
                date_of_booking=datetime.now().date(),
                date_of_issuing=date_of_issuing,
                due_date=due_date,
                number_of_days=number_of_days,
                quantity_issued=quantity,
                rent=db_item.rent,
                total_rent=total_rent,
                balance=total_rent
            )
            session.add(rental)
            session.commit()

            rental_ids.append(rental.rental_id)  # Store the generated rental ID

        print(f"Rental finalized with IDs: {rental_ids}")  # Debugging
        return jsonify({"success": True, "rental_id": rental_ids[-1]}), 200  # Return the last rental_id
    except Exception as e:
        session.rollback()
        print("Error:", str(e))  # Debugging
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/bill_summary/<int:rental_id>")
def bill_summary(rental_id):
    try:
        rental = session.query(Rental).filter_by(rental_id=rental_id).all()  # Fetch as a list

        if not rental:
            return "No rental found for this ID.", 404

        total_rent = sum(r.total_rent for r in rental)  # Calculate total rent

        return render_template("bill_summary.html", rentals=rental, total_rent=total_rent)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route("/finalize_bill", methods=["POST"])
def finalize_bill():
    try:
        advance = float(request.form.get("advance"))
        rental_id = request.form.get("rental_id")  # Retrieve from form

        if not rental_id:
            return "Rental ID is missing", 400

        rental = session.query(Rental).filter_by(rental_id=rental_id).first()

        if not rental:
            return "No rental found for this ID", 404

        rental.advance = advance
        rental.balance = rental.total_rent - advance
        session.commit()

        return redirect(url_for("bill_summary", rental_id=rental_id))  # Redirect based on rental_id
    except Exception as e:
        session.rollback()
        return f"An error occurred: {str(e)}", 500



@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        name = request.form.get("name")
        phone_number = request.form.get("phone_number")
        
        try:
            # Check if user already exists
            existing_user = session.query(User).filter_by(phone_number=phone_number).first()
            if existing_user:
                return render_template("add_user.html", error="User with this phone number already exists.")
            
            # Add new user
            new_user = User(name=name, phone_number=phone_number)
            session.add(new_user)
            session.commit()
            
            return redirect(f"/rental_details/{new_user.user_id}")
        except Exception as e:
            session.rollback()
            return render_template("add_user.html", error=f"Error: {e}")
    
    return render_template("add_user.html")


@app.route("/rental_details/<int:user_id>", methods=["GET", "POST"])
def rental_details(user_id):
    if request.method == "POST":
        item_id = request.form.get("item_id")
        quantity_issued = int(request.form.get("quantity_issued"))
        date_of_booking = request.form.get("date_of_booking")
        due_date = request.form.get("due_date")
        advance = float(request.form.get("advance"))

        # Fetch item details
        item = session.query(Item).filter_by(item_id=item_id).one_or_none()
        if not item or item.quantity < quantity_issued:
            return render_template("rental_details.html", user_id=user_id, error="Invalid item or insufficient quantity.")

        # Calculate rent and balance
        total_rent = item.rent * quantity_issued
        balance = total_rent - advance

        # Add rental entry
        new_rental = Rental(
            user_id=user_id,
            item_id=item_id,
            date_of_booking=date_of_booking,
            due_date=due_date,
            quantity_issued=quantity_issued,
            rent=item.rent,
            advance=advance,
            total_rent=total_rent,
            balance=balance
        )
        item.quantity -= quantity_issued
        item.issued_quantity += quantity_issued

        session.add(new_rental)
        session.commit()
        return render_template("rental_success.html", rental=new_rental)

    # Render rental details form
    items = session.query(Item).all()
    return render_template("rental_details.html", user_id=user_id, items=items)


if __name__ == "__main__":
    app.run(debug=True)
