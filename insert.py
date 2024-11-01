import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URI = 'sqlite:///schedules.db'
Base = declarative_base()

# Schedule model
class Schedule(Base):
    __tablename__ = 'schedule'
    
    id = Column(Integer, primary_key=True)
    play_music_folder = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=True)
    days = Column(String, nullable=False)  # Store days as a comma-separated string

# Create the database if it does not exist
def create_database():
    if not os.path.exists('schedules.db'):
        engine = create_engine(DATABASE_URI)
        Base.metadata.create_all(engine)
        print("Database created.")
    else:
        print("Database already exists.")

# Function to insert a new schedule
def insert_schedule(play_music_folder, start_time, end_time, days):
    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)

    # Convert days list to a comma-separated string
    days_str = ','.join(days)

    try:
        with Session() as session:
            # Convert start_time and end_time to time objects
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time() if end_time else None

            # Create a new schedule entry
            new_schedule = Schedule(
                play_music_folder=play_music_folder,
                start_time=start_time_obj,
                end_time=end_time_obj,
                days=days_str  # Store as a plain string
            )

            session.add(new_schedule)
            session.commit()
            print("New schedule added.")
    except Exception as e:
        print(f"Error inserting schedule: {e}")

def delete_schedule(schedule_id):
    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)

    try:
        with Session() as session:
            schedule_to_delete = session.query(Schedule).filter(Schedule.id == schedule_id).first()
            if schedule_to_delete:
                session.delete(schedule_to_delete)
                session.commit()
                print(f"Schedule with ID {schedule_id} has been deleted.")
            else:
                print(f"No schedule found with ID {schedule_id}.")
    except Exception as e:
        print(f"Error deleting schedule: {e}")

def delete_all_schedules():
    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)

    try:
        with Session() as session:
            session.query(Schedule).delete()  # Deletes all rows in the Schedule table
            session.commit()
            print("All schedules have been deleted.")
    except Exception as e:
        print(f"Error deleting schedules: {e}")

if __name__ == "__main__":
    create_database()
    # Example usage
    insert_schedule(
        'C:/Users/admin/OneDrive - DePaul University/OOP/Desktop(1)/mp3/02. Prabhatiya', 
        '00:03', 
        '00:15', 
        ['Monday', 'Friday', 'Thursday']
    )
