echo "Executing create_dependency_zip.sh"

cd ..
rm -rf ./terraform/$DEPENDENCIES_PATH

REQUIREMENTS_FILE=./terraform/files/requirements.txt
echo "Creating requirements: $REQUIREMENTS_FILE"
poetry export -f requirements.txt --output $REQUIREMENTS_FILE
pip install -r $REQUIREMENTS_FILE --target ./terraform/$DEPENDENCIES_PATH
