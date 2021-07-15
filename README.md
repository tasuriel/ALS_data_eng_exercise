# ALS---Data-Engineering-Exercise - Instructions


##Summary:

The python script included pulls from CRM data from three AWS files: "cons.csv", "cons_email.csv", and "cons_email_chapter_subscription.csv". It then stores those datasets to a working directory. This information is then used to create a "people.csv", with emails and some related metadata, and "acquisition_facts.csv", which summarizes email aquisitions by date. Both are published to the working directory


##Instructions

These instructions assume that you have some command line python package installer (such as pip) and python3.

1. Create a working directory and download requirements.txt and ALS_data_engineering_ex.py

2. Install packages in requirements.txt in command line.
  e.g.
``` bash
baseDir="<working directory>"
cd "${baseDir}"
pip install -r requirements.txt
```
3. In command line run python script with the working directory
  e.g.
 ``` bash
baseDir="<working directory>"
python3 -u ALS_data_engineering_ex.py "${baseDir}"
```
  
  
##To Note About The Output Files:
  
Create date is earliest date listed in cons or cons_email file. Updated date is most recent date available for a given constituent accross all files. Acquired date is considered the create date as defined above.

Some Things For Further Data Cleaning:
* Certain columns look like random strings of letters.
    * in Cons: Salutation, Title, Employer, occupation, subsource
    * in cons_email: canonical_local_part, double_validation
* Gender - looks like letters of the alphabet, there are 26 distinct types.
* People file includes folks who are banned, emails that are not the primary email, and emails that have or haven't been validated
* It is unclear what Status in cons and cons_email means.
* Dates stretch to before the internet was inveted, 1970
