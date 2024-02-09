import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv("Youtube_comments.csv")

idtofind = 2

# Filter the DataFrame by ID
filtered_df = df.loc[df['ID'] == idtofind]

# Check if data was found
if not filtered_df.empty:
  print(filtered_df.to_string(index=False))

else:
  print(f"ID {idtofind} not found in the CSV file.")
