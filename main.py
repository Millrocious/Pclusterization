import os
import shutil
import subprocess
import pandas as pd

from fastapi import FastAPI
from starlette.responses import FileResponse

from schemas import Iris
from notebook import notebookapp


app = FastAPI()


@app.post("/api/dataset")
async def add_iris(item: Iris):
    new_row_dict = item.dict()
    df = pd.read_csv('Iris_test.csv')

    new_id = df['Id'].max() + 1
    new_row_dict['Id'] = new_id

    df = df.append(new_row_dict, ignore_index=True)
    df.to_csv('Iris.csv', index=False)

    return item


# Get the port number of a running notebook server
def get_notebook_server_port():
    servers = list(notebookapp.list_running_servers())
    if not servers:
        raise Exception("No running notebook server found")
    return servers[0]['port']


# Start the Jupyter Notebook server
def start_notebook_server(token):
    cmd = ['jupyter', 'notebook', '--no-browser', f"--NotebookApp.token={token}"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Failed to start Jupyter Notebook server: {error}")
    return output.decode().strip()


# Run a Jupyter Notebook file and return its output as HTML
@app.get("/run_notebook")
async def run_notebook():
    notebook_path = 'Iris-clusterization.ipynb'

    # Start the notebook server if it's not running
    try:
        port = get_notebook_server_port()
    except:
        start_notebook_server(token="verystrongtoken")
        port = get_notebook_server_port()

    # Use the current working directory to store the executed notebook file and output HTML file
    cwd = os.getcwd()
    output_path = os.path.join(cwd, 'Iris-clusterization.ipynb')
    html_path = os.path.join(cwd, 'Iris-clusterization.html')

    # Execute the notebook file and save output as HTML
    os.system(
        f"jupyter nbconvert --execute --ExecutePreprocessor.timeout=-1 --to notebook --output {output_path} {notebook_path} --ExecutePreprocessor.allow_errors=True --ExecutePreprocessor.kernel_name=python --NotebookApp.allow_origin=* --NotebookApp.token={'verystrongtoken'} --NotebookApp.disable_check_xsrf=True --NotebookApp.port={port}")
    os.system(f"jupyter nbconvert --to html --output-dir {cwd} {output_path}")

    # Return the HTML file as a FastAPI response
    return FileResponse(html_path)
