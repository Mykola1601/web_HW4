
# baze immage
from python:alpine3.17


# env variable
ENV APP /web_HW4

# working directory
WORKDIR $APP

# volume
VOLUME /storage

# copy my project
COPY . .

# run requirements
RUN pip install -r requirements.txt

# port set
EXPOSE 3000:3000

ENTRYPOINT ["python", "main.py" ]