FROM python:3.10

WORKDIR /toolsDocker

COPY requiremnts.txt .
RUN pip install -r requiremnts.txt
RUN pip3 install python-dotenv

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# RUN pip install django-cors-headers

# RUN pip install django-webpack-loader
COPY . .

CMD ["python", "manage.py" ,"runserver"]
