import pandas as pd

data = pd.read_json("./test-data.json")
print(data)
print([*data])