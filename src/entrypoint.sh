#!/bin/bash
cd /streamlit
pip3 install -r $STREAMLIT_REQUIREMENTS
python3 -m streamlit run --logger.level=debug --server.port=8080 --server.address=0.0.0.0 --server.runOnSave=true --server.fileWatcherType=poll $@ 2>&1