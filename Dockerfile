FROM python:3.12-alpine

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY scheduler.py ./

# Unlike test image, modules are not copied in
# Instead, they are mounted at ./modules via compose to allow easy addition
# of new modules

EXPOSE 5000
ENTRYPOINT [ "flask", "--app", "main", "run", "--host=0.0.0.0"]