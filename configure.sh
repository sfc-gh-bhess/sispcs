#!/bin/bash

# Prompt user for input
read -p "What is the image repository URL (SHOW IMAGE REPOSITORIES IN SCHEMA)? " repository_url
read -p "What is the stage location for the Streamlit source? " streamlit_stage
read -p "What is the path to the main file for Strealmit in that stage? " streamlit_main
read -p "What is the path to the requirements file for Strealmit in that stage? " streamlit_requirements
read -p "What warehouse can the Streamlit app use? " warehouse
read -p "What is the stage location for the Python packages? " pythonpath_stage

# Paths to the files
makefile="./Makefile"
streamlit_file="./streamlit.yaml"

# Copy files
cp $makefile.template $makefile
cp $streamlit_file.template $streamlit_file

# Replace placeholders in Makefile file using | as delimiter
sed -i "" "s|<<repository_url>>|$repository_url|g" $makefile

# Replace placeholders in Streamlit file using | as delimiter
sed -i "" "s|<<repository_url>>|$repository_url|g" $streamlit_file
sed -i "" "s|<<warehouse_name>>|$warehouse|g" $streamlit_file
sed -i "" "s|<<streamlit_stage>>|$streamlit_stage|g" $streamlit_file
sed -i "" "s|<<streamlit_main>>|$streamlit_main|g" $streamlit_file
sed -i "" "s|<<streamlit_requirements>>|$streamlit_requirements|g" $streamlit_file
sed -i "" "s|<<pythonpath_stage>>|$pythonpath_stage|g" $streamlit_file


echo "Placeholder values have been replaced!"
