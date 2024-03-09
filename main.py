from config import config
from utils import create_database, save_data_to_database, user_interactive

if __name__ == '__main__':

    employers_ids = [
                     ]

    params = config()

    create_database("course_work_5", params)
    save_data_to_database(employers_ids, "course_work_5", params)
    user_interactive("course_work_5")