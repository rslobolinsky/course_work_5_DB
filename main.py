from config import config
from utils import create_database, save_data_to_database, user_interactive

if __name__ == '__main__':

    employers_ids = ['5920492',
                     '3643187',
                     '5873504',
                     '9498120',
                     '6146301',
                     '9895958',
                     '593501',
                     '3711736',
                     '6157619',
                     '10536354',
                     ]

    params = config()

    create_database("course_work_5", params)
    save_data_to_database(employers_ids, "course_work_5", params)
    user_interactive("course_work_5")