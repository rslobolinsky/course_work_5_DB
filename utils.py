import psycopg2

from classes import Employer, Vacancy, DBManager


def create_database(database_name: str, params: dict) -> None:
    """Создает базу данных"""

    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f'DROP DATABASE IF EXISTS {database_name}')
    cur.execute(f'CREATE DATABASE {database_name}')

    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE employers (
                employer_id SERIAL PRIMARY KEY,
                employer_name VARCHAR(255),
                employer_vacancies INTEGER,
                employer_url TEXT 
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                employer_id INT REFERENCES employers(employer_id),
                vacancy_name TEXT,
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(10),
                vacancy_url TEXT
            )
        """)

    conn.commit()
    conn.close()


def save_data_to_database(employers_ids: list, database_name, params: dict):
    """Сохраняет данный в базу данных"""

    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        for employer in Employer.initiate_from_hh(employers_ids):
            employer_name = employer.employer_name
            employer_vacancies = employer.employer_vacancies
            employer_url = employer.employer_url
            emp_id = employer.employer_id
            cur.execute("""
                INSERT INTO employers (employer_name, employer_vacancies, employer_url)
                VALUES (%s, %s, %s)
                RETURNING employer_id
                """, (employer_name, employer_vacancies, employer_url)
            )
            employer_id = cur.fetchone()[0]
            for vacancy in Vacancy.initiate_from_hh(emp_id):
                vacancy_name = vacancy.vacancy_name
                salary_from = vacancy.salary_from
                salary_to = vacancy.salary_to
                currency = vacancy.currency
                vacancy_url = vacancy.vacancy_url
                cur.execute("""
                    INSERT INTO vacancies (employer_id, vacancy_name, salary_from, salary_to, currency, vacancy_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (employer_id, vacancy_name, salary_from, salary_to, currency, vacancy_url)
                )

        conn.commit()
        conn.close()

def user_interactive(database_name):
    """Интерактив с пользователем"""

    while True:
        print("1. Вывести список работодателей в базе с количеством вакансий")
        print("2. Вывести список всех вакансий в базе")
        print("3. Вывести среднюю зарплату по всем вакансиям")
        print("4. Вывести список вакансий с зарплатой выше средней по базе")
        print("5. Вывести список вакансий с ключевым словом в названии")
        print("0. Выход")
        user_input = int(input("Введите ваш выбор: "))
        if user_input == 1:
            DBManager.get_companies_and_vacancies_count(database_name)
            break
        elif user_input == 2:
            DBManager.get_all_vacancies(database_name)
            break
        elif user_input == 3:
            DBManager.get_avg_salary(database_name)
            break
        elif user_input == 4:
            DBManager.get_vacancies_with_higher_salary(database_name)
            break
        elif user_input == 5:
            while True:
                user_keyword = input("Введите ключевое слово: ")
                if not user_keyword:
                    print("Вы ввели пустой запрос")
                    continue
                else:
                    DBManager.get_vacancies_with_keyword(database_name, user_keyword)
                    break
            break
        elif user_input == 0:
            print("До свидания!")
            break
        else:
            print("Введите число от 0 до 5")
            continue