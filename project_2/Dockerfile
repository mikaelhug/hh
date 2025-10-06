FROM python:3.11
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
RUN groupadd -g 1000 django
RUN useradd -u 1000 -g django django

RUN mkdir -p /hh
WORKDIR /hh
COPY ./hh /hh/

RUN pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt

USER django
EXPOSE 8000 3000
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:3000", "manage.py", "runserver", "0.0.0.0:8000"]