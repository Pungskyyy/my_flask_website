from app import app, db, User  # pastikan app.py punya objek app, db, dan class User

with app.app_context():
    users = User.query.all()

    print("Daftar user:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
