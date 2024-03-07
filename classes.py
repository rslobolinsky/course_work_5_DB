from config import config
import psycopg2
import requests

from config import employers_url, vacancies_url


class Employer:
    def __init__(self, employer_id, employer_name: str, employer_vacancies: int, employer_url: str):
        self.employer_id = employer_id
        self.employer_name = employer_name
        self.employer_vacancies = employer_vacancies
        self.employer_url = employer_url

    @classmethod
    def initiate_from_hh(cls, em_ids: list[str]):
        """Создает список с экземплярами класса по заданным параметрам"""
        employers_list = []
        for em_id in em_ids:
            try:
                response = requests.get(url=f"{employers_url}{em_id}").json()
                employer_id = response['id']
                employer_name = response['name']
                employer_vacancies = response['open_vacancies']
                employer_url = response['alternate_url']
                employer = Employer(employer_id, employer_name, employer_vacancies, employer_url)
                employers_list.append(employer)
            except KeyError:
                raise KeyError('id not found')
        return employers_list


class Vacancy:
    """Класс Вакансий"""

    def __init__(self,
                 employer_id: str,
                 vacancy_id: int,
                 vacancy_name: str,
                 salary_from: int,
                 salary_to: int,
                 currency: str,
                 vacancy_url: str):
        self.employer_id = employer_id
        self.vacancy_id = vacancy_id
        self.vacancy_name = vacancy_name
        self.salary_from = self.validate_salary_from(salary_from)
        self.salary_to = self.validate_salary_to(salary_from, salary_to)
        self.currency = currency
        self.vacancy_url = vacancy_url

    @classmethod
    def initiate_from_hh(cls, employer_id: str):
        """Создает список с экземплярами класса по заданным параметрам"""

        params = {
            'page': 0,
            'per_page': 100,
            'only_with_salary': True,
            'employer_id': employer_id
        }
        vacancies_list = []
        employer_vacancies = requests.get(url=vacancies_url, params=params).json()
        for unit in employer_vacancies['items']:
            emp_id = employer_id
            vacancy_id = unit['id']
            vacancy_name = unit['name']
            salary_from = unit['salary']['from']
            salary_to = unit['salary']['to']
            currency = unit['salary']['currency']
            vacancy_url = unit['alternate_url']
            vacancy = Vacancy(emp_id, vacancy_id, vacancy_name, salary_from, salary_to, currency, vacancy_url)
            vacancies_list.append(vacancy)
        return vacancies_list

    @staticmethod
    def validate_salary_from(salary):
        """Возвращает 0 если не указана минимальная зарплата"""
        if not salary:
            return 0
        return salary

    @staticmethod
    def validate_salary_to(salary_from, salary_to):
        """Возвращает максимальную зарплату равную минимальной, если максимальная не указана"""

        if not salary_to:
            salary_to = salary_from
        return salary_to


class DBManager:

    @classmethod
    def get_companies_and_vacancies_count(cls, database_name):
        """Получает список всех компаний и количество вакансий у каждой компании"""

        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT employers.employer_name as employer, COUNT(*)
                FROM employers
                JOIN vacancies using (employer_id)
                GROUP BY employer
                """)
            response = cur.fetchall()
        for r in response:
            print(f"{r[0]} - {r[1]} вакансий")
        conn.close()

    @classmethod
    def get_all_vacancies(cls, database_name):
        """Получает список всех вакансий с указанием названия компании,
            названия вакансии и зарплаты и ссылки на вакансию"""

        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                employers.employer_name,
                vacancies.vacancy_name,
                vacancies.salary_from,
                vacancies.salary_to,
                vacancies.vacancy_url
                FROM employers
                JOIN vacancies USING (employer_id)
                """)
            response = cur.fetchall()
        for r in response:
            print(f"{r[0]} / {r[1]} / {r[2]}-{r[3]} RUR / ссылка {r[4]}")

    @classmethod
    def get_avg_salary(cls, database_name):
        """Получает среднюю зарплату по вакансиям"""

        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((salary_from + salary_to)/2)
                FROM vacancies
                """)
            response = cur.fetchall()
        print(f"Средняя зарплата по всем вакансиям базы данных - {round(response[0][0])} рублей")

    @classmethod
    def get_vacancies_with_higher_salary(cls, database_name):
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям"""

        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            cur.execute("""SELECT 
                employers.employer_name,
                vacancies.vacancy_name,
                vacancies.salary_from,
                vacancies.salary_to,
                vacancies.vacancy_url
                FROM employers
                JOIN vacancies USING (employer_id)
                WHERE ((vacancies.salary_from + vacancies.salary_to)/2) >
                (SELECT AVG((salary_from + salary_to)/2) FROM vacancies)""")
            response = cur.fetchall()
        cls.get_avg_salary(database_name)
        print("\nЗарплата по данным вакансиям выше средней по всей базе:\n")
        for r in response:
            print(f"{r[0]} / {r[1]} / {r[2]}-{r[3]} RUR / ссылка {r[4]}")

    @classmethod
    def get_vacancies_with_keyword(cls, database_name, query):
        """Получает список всех вакансий, в названии которых содержатся переданные в метод слова"""

        params = config()
        conn = psycopg2.connect(dbname=database_name, **params)
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT
                employers.employer_name,
                vacancies.vacancy_name,
                vacancies.salary_from,
                vacancies.salary_to,
                vacancies.vacancy_url
                FROM employers
                JOIN vacancies USING (employer_id)
                WHERE vacancies.vacancy_name LIKE '%{query.lower()}%'
                """)
            response = cur.fetchall()
        if not response:
            print("\nПо вашему запросу ничего не найдено\n")
        else:
            print("\nПо вашему запросу найдены следующие вакансии:\n")
            for r in response:
                print(f"{r[0]} / {r[1]} / {r[2]}-{r[3]} RUR / ссылка {r[4]}")
