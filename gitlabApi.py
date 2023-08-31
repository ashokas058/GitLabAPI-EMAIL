import smtplib
from datetime import datetime,time
import sys
import requests
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
 
#---------------------------------------------------
company_name="" #update here
baseUrl="https://gitlab.com/api/v4/projects"
projectId= #provide Gitlab project number/ID
TOKEN=''     #generate new Token with permission to read
sender_email = ''  # update here
sender_accountpass='' 
smtp_server=''   #for Gmail - smtp.gmail.com
smtp_port=       #587
receiver_email = '' 

 
#------------------------------------------------
def getCommitPath(commit_id):
  jsonData=requests.get(baseUrl+'/'+str(projectId)+'/repository/commits/'+commit_id+'/diff',
  headers={'PRIVATE-TOKEN':TOKEN}).json()
  path=""
  for data in jsonData:
    path+=data['new_path']+"<br>"
  return path
 
def getCommitByBranch(params):
  return requests.get(baseUrl+'/'+str(projectId)+'/repository/commits',
  headers={'PRIVATE-TOKEN':TOKEN},params=params).json()
 
 

def getLastbuildate():          
    file_path ='date_val'
 
    try:
        with open(file_path, 'r') as file:
            contents = file.read()
            return contents
    except FileNotFoundError:
        print("File not found.")
 
#-------------------------------------------
try:
    buildStatus = sys.argv[1]
    buildNumber = sys.argv[2]
    branch = sys.argv[3]
    projectName = sys.argv[4]
    apiName = sys.argv[5].strip('"')
    print(apiName)

    # lastBuildTime=sys.argv[6]

    # ----------------------------------------------

    total = 0
    committer = ""
    message = ""
    url = ""
    lastBuildTime = getLastbuildate()  # update your custom datatime here or update in date_val file(project root).
    print(lastBuildTime)
    subject = "Build :-" + buildStatus + "[ " + buildNumber + "]"
    params = {'since': lastBuildTime, 'ref_name': branch, 'path': apiName}

    table_rows = ''
    for data in getCommitByBranch(params):
        print(data)
        row = f'''
        <tr>
          <td>{data['committer_name']}</td>
          <td>{data['message']}</td>
          <td>{getCommitPath(data['id'])}</td>
          <td><a href={data['web_url']}>git commit info</a></td>
          <td>{data['committed_date']}</td>
        </tr>
        '''
        table_rows += row
        total += 1

    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
      <title>Build Status</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          margin: 0;
          padding: 0;
        }}

        p {{
          text-align: center;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          color: #333;
          margin-top: 20px;
        }}

        #logo {{
          display: block;
          margin: 0 auto;
          max-width: 200px;
          height: auto;
          margin-bottom: 20px;
        }}

        table {{
          margin: 0 auto;
          border-collapse: collapse;
          width: 80%;
        }}

        th {{
          padding: 10px;
          text-align: left;
          border-bottom: 1px solid #ddd;
        }}

        td {{
          padding: 10px;
          text-align: left;
          border: 1px solid #ddd;
        }}

        th.project-name {{
          text-align: left;  /* Align to the right */
          background-color: #f2f2f2;
        }}

        th.build-status {{
          text-align: left;  /* Align to the right */
          background-color: #f2f2f2;
        }}
        tr:nth-child(even) {{
          background-color: #f9f9f9;
        }}

        tr:nth-child(odd) {{
          background-color: #e9e9e9;
        }}

        tr:hover {{
          background-color: #f5f5f5;
        }}

        .date-column {{
          font-weight: bold;
        }}
        .company-name {{
          font-size: 24px;
          font-weight: bold;
          color: #c92611;
        }}

      </style>
    </head>
    <body>
    <h1 class="company-name">{company_name}<span style="color: #333;"> Build-Report</span></h1>
      <table>
        <tr>
          <th class="project-name" colspan="5">Project Name:- {projectName}</th>
        </tr>
        <tr>
          <th class="build-status" colspan="5">Build Status:- {buildStatus}</th>
        </tr>
        <tr>
          <th class="build-status" colspan="5">Branch:- {branch}</th>
        </tr>
        <tr>
          <th class="build-status" colspan="5">Total:-{total}</th>
        </tr>
        <tr>
          <th>Commiter</th>
          <th>Changes</th>
          <th>Changed-files</th>
          <th>Url</th>
          <th>CommitDate</th>
        </tr>
        {table_rows}
      </table>
    </body>
    </html>
    '''
    # Create a multipart message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Attach HTML content
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_accountpass)
        server.sendmail(sender_email, receiver_email, message.as_string())

except IndexError:
    print("provide BuildStatus, BuildNumber, Branch, projectName")