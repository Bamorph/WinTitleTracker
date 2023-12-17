import win32gui
import time
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class WindowActivity(Base):
    __tablename__ = 'window_activity'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    duration = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_active_window_title():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds"

def main():
    engine = create_engine('sqlite:///window_activity.db', echo=True)  # Use your desired SQLite database file name
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    current_title = get_active_window_title()
    start_time = time.time()

    while True:
        time.sleep(1)  # Adjust the interval as needed
        new_title = get_active_window_title()

        if new_title != current_title:
            end_time = time.time()
            duration = end_time - start_time

            if current_title.strip():  # Check if the title is not blank or contains only whitespace
                existing_record = session.query(WindowActivity).filter_by(title=current_title).first()

                if existing_record:
                    existing_record.duration += duration
                    existing_record.modified_at = datetime.utcnow()
                else:
                    window_activity = WindowActivity(title=current_title, duration=duration)
                    session.add(window_activity)

                session.commit()
                print("Window Title:", current_title, "| Duration:", format_duration(duration))

            current_title = new_title
            start_time = time.time()

if __name__ == "__main__":
    main()
