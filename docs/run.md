To run the Docker image of the Nautobot, including the template application, do the following:
`poetry shell`
- If it is not installed, run first `poetry self add poetry-plugin-shell`
`invoke build` # build the neccecary images
`invoke start` # run container in detached mode

To stop the containers, do
`invoke stop`
