import streamlit as st
import datetime
from spcs_helpers.connection import session
from snowflake.snowpark import Session
from snowflake.snowpark import functions as f

from streamlit.web.server.websocket_headers import _get_websocket_headers
user = _get_websocket_headers().get("Sf-Context-Current-User") or "Visitor"
st.set_page_config(layout="wide")

@st.cache_resource
def connect_to_snowflake():
    return session()

@st.cache_data
def top_clerks(_sess: Session, begin, end, topn):
    return sess.table('snowflake_sample_data.tpch_sf10.orders') \
                .filter(f.col('O_ORDERDATE') >= begin) \
                .filter(f.col('O_ORDERDATE') <= end) \
                .group_by(f.col('O_CLERK')) \
                .agg(f.sum(f.col('O_TOTALPRICE')).as_('CLERK_TOTAL')) \
                .order_by(f.col('CLERK_TOTAL').desc()) \
                .limit(topn) \
                .to_pandas()

st.sidebar.header(f"Hello, {user}")
st.title("Top Clerks")
st.subheader("Let's find the top clerks by total sales in a date range")

c1,c2 = st.columns(2)
begin = c1.date_input("Beginning of window", 
                      value=datetime.date.fromisoformat("1993-01-01"),
                      min_value=datetime.date.fromisoformat("1992-01-01"),
                      max_value=datetime.date.fromisoformat("1998-08-02"))

end = c2.date_input("End of window", 
                      value=datetime.date.fromisoformat("1993-12-31"),
                      min_value=begin,
                      max_value=datetime.date.fromisoformat("1998-08-02"))

topn = st.slider("TopN", value=10, min_value=1, max_value=30)

sess = connect_to_snowflake()

df = top_clerks(sess, begin, end, topn)
st.dataframe(df)

st.divider()

import os
from streamlit.watcher.util import path_modification_time
fnames = [os.path.join(r,file) for (r,d,f) in os.walk(".") for file in f]
st.json(fnames)
ff = st.selectbox("Choose a file", options=fnames)
c1,c2,c3,c4 = st.columns(4)
c1.metric("Size", value=os.path.getsize(ff))
c2.metric("Create Time", value=datetime.datetime.fromtimestamp(os.path.getctime(ff)).strftime('%Y-%m-%d %H:%M:%S'))
# c3.metric("Modified Time", value=datetime.datetime.fromtimestamp(os.path.getmtime(ff)).strftime('%Y-%m-%d %H:%M:%S'))
c3.metric("Modified Time", value=datetime.datetime.fromtimestamp(path_modification_time(ff)).strftime('%Y-%m-%d %H:%M:%S'))
c4.metric("Now", value=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
contents = open(ff, 'r').read()
st.code(contents)