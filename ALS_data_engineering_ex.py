import pandas as pd
import numpy as np
import sys
import os

#Get working directory as input and set it
# if len(sys.argv) == 2:
#     working_dir = sys.argv[1]
working_dir = '/Users/tsuriel/Desktop/ALS_data_engineering'
working_dir = working_dir + "/"
os.chdir(working_dir)

# import data from AWS if not available in working directoy
for doc in ["cons.csv", "cons_email.csv", "cons_email_chapter_subscription.csv"]:
    if os.path.exists(working_dir+doc):
        exec(f"""{doc[:-4]} = pd.read_csv('{doc}')""")
    else:
        cons = pd.read_csv("https://als-hiring.s3.amazonaws.com/fake_data/2020-07-01_17%3A11%3A00/"+doc)


#Narrow To Only Necessary Columns for people and acquisition_facts files
cons = cons[['cons_id', 'source', 'create_dt', 'modified_dt',]]
cons = cons.rename({"create_dt":"cons_create_dt", "modified_dt":"cons_modified_dt"},
                   axis=1)

cons_email = cons_email[['cons_id', 'cons_email_id', 'email', 'create_dt', 'modified_dt']]
cons_email = cons_email.rename({"create_dt":"ce_create_dt", "modified_dt":"ce_modified_dt"},
                               axis=1)

cons_email_chapter_subscription = cons_email_chapter_subscription[['cons_email_id', 'chapter_id', 'isunsub', 'unsub_dt', 'modified_dt']]
cons_email_chapter_subscription = cons_email_chapter_subscription.rename({"create_dt":"ces_create_dt", "modified_dt":"ces_modified_dt"},
        axis=1)


# Merge Constituent, email, and chapter subscription data.
df = cons.merge(cons_email, on='cons_id', how='outer')
df = df.merge(cons_email_chapter_subscription, on='cons_email_id', how='outer')
df = df[['cons_id', 'cons_email_id', 'email', 'source', 'chapter_id', 'isunsub', 'cons_create_dt', 'ce_create_dt', 'cons_modified_dt', 'ce_modified_dt', 'unsub_dt', 'ces_modified_dt',]]

# Remove constituents with no available emails, and where chapter ID is not One. No Chapter info or is_unsub info is classified as chapter_id of 1 and is_unsub of 0.
df = df[~df['email'].isna()]
df['chapter_id'] = df['chapter_id'].replace({np.nan:1})
df['isunsub'] = df['isunsub'].replace({np.nan:0})
df = df[df['chapter_id'].eq(1)]


# Convert date time columns to date time.
for col in df.columns:
    if col[-3:]=="_dt":
        df[col] = pd.to_datetime(df[col].apply(lambda x: x.split(",")[1].strip() if x not in (np.nan, None, float('nan')) else x))


#Pick earliest create date available accross all files as created_dt
df['created_dt'] = df.apply(lambda row: min([row['cons_create_dt'], row['ce_create_dt'],]), axis=1)
#Pick latest date of any available as updated_dt
df['updated_dt'] = df.apply(lambda row: max([row['cons_modified_dt'], row['ce_modified_dt'],
    row['unsub_dt'], row['ces_modified_dt']]),
    axis=1)

#Reduce to necessary columns, drop duplicates, match data_schema as given in instructions.
df = df[['email', 'source', 'isunsub', 'created_dt', 'updated_dt']]
df = df.rename({"source":"code", "isunsub":"is_unsub"}, axis=1)
df = df.drop_duplicates()

#Publish people table
df.to_csv("people.csv", index=False, header=True)

#Using the people table, count how many emails were created on a given day. Publish acquisition_facts table, match data_schema as given.
df = df.groupby('created_dt').agg({"email":"count"}).reset_index()
df = df.rename({"created_dt":"acquisition_date", "email":"acquisitions"}, axis=1).sort_values(by='acquisition_date').copy()
df.to_csv("acquisition_facts.csv", index=False, header=True)
