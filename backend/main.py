from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
import stripe
import os

# PostgreSQL connection string - apne credentials daalo
DATABASE_URL = "postgresql://postgres:passwordmacbook@localhost/online_courses"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Stripe secret key (test mode)
from dotenv import load_dotenv
load_dotenv()

stripe.api_key = os.getenv("sk_test_51RQruyFdd1LL5iKDJv35t8eC2aWUPbEMlh20Y4cfyWyISy6fbSOCIZxGaBjLsUQpgxjKgR3XSB0vUISwK1yAjLPt00e8dIsHMk")

# Course model
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Integer, nullable=False)  # price in rupees

# Create tables agar exist nahi karte toh
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production mein domain specify karo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Server running"}

@app.get("/courses")
def get_courses():
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        return [{"id": c.id, "title": c.title, "price": c.price} for c in courses]
    finally:
        db.close()

@app.post("/create-checkout-session/{course_id}")
def create_checkout_session(course_id: int):
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "inr",
                    "product_data": {
                        "name": course.title,
                    },
                    "unit_amount": course.price * 100,  # paise mein
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://127.0.0.1:5500/frontend/success.html",
            cancel_url="http://localhost:5500/cancel.html",
        )
        return {"id": session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()














