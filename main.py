from config import config
from utils import create_database, save_data_to_database, user_interactive

if __name__ == '__main__':
    employers_ids = [
                     ]

    params = config()

    create_database("Course_Work_5", params)
    save_data_to_database(employers_ids, "Course_Work_5", params)
    user_interactive("Course_Work_5")