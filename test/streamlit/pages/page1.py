import streamlit as st 

st.title("Page 1")

from streamlit.source_util import get_pages
pages = get_pages("../app.py")

st.json(pages)

import os
import datetime
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
