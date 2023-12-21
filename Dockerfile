FROM python:3.10
EXPOSE 8080
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install snowflake-connector-python snowflake-snowpark-python pandas numpy datetime wheel
COPY streamlit-1.29.0-py2.py3-none-any.whl .
RUN pip3 install streamlit-1.29.0-py2.py3-none-any.whl
RUN pip3 uninstall oscrypto -y
RUN pip3 install oscrypto@git+https://github.com/wbond/oscrypto.git@d5f3437ed24257895ae1edd9e503cfb352e635a8

# Move existing site-packages to site-packages-orig, create new site-packages,
#   and setup Python to know that
RUN mv /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages-orig
RUN mkdir /usr/local/lib/python3.10/site-packages
RUN mkdir /usr/local/lib/python3.10/sitecustomize
RUN echo "import sys\nsys.path.insert(0, '/usr/local/lib/python3.10/site-packages-orig')\n" > /usr/local/lib/python3.10/sitecustomize/__init__.py

COPY src/. .
RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]
