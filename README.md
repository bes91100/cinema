pip install -r requirements.txt
python manage.py makemigrations cinema
python manage.py migrate
python manage.py createsuperuser
python manage.py generate_data
python manage.py runserver

cd client
npm install
npm run dev


Сайт: http://localhost:5173
