import requests

username = 'hhhscvx'
password = 'RomKir10'
base_url = 'http://127.0.0.1:8000/api'

r = requests.get(f'{base_url}/courses/')  # извлечь все курсы
courses = r.json()

available_courses = ', '.join([course['title'] for course in courses])  # title`ы курсов через запятую
print(f'Доступные курсы: {available_courses}')

for course in courses:
    course_id = course['id']
    course_title = course['title']
    r = requests.post(f'{base_url}/courses/{course_id}/enroll/',
                      auth=(username, password))
    if r.status_code == 200:
        print(f'Успешное зачисление на курс {course_title}')
