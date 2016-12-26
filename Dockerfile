FROM dinocloud/opencv:1.0.0

COPY vader /vader
RUN cd /vader && pip install -r requirements.txt

CMD "python /vader/app.py --tenant $TENANT_ID --key $TENANT_KEY"

