import requests
import json
import pandas as pd
import os
import urllib.request
import time
import urllib3
urllib3.disable_warnings()

URLlist_ID ="28815B6A-775F-49A0-BDA2-28C673D14E98"
job_ID = "6BEAF7B9-CE8C-4F8C-9D2C-2753686B3AC9"  #https://192.168.2.175:8082/api/jobs
MC_info = "192.168.2.175"
authid="YWRtaW46U3ltNG5vdyE=" #base64 encode "username:password"
McUpurl="https://"+MC_info+":8082/api/policies/"+URLlist_ID+"/content"
proxysgurl='https://192.168.2.170:8082'
auth_user="admin"
auth_passwd="Master00"


print("Download starting...")
#---- download from USOM
try:
    response = urllib.request.urlopen('https://www.usom.gov.tr/url-list.txt',timeout=60)
    data = response.read()
    filename = "usom_download.txt"
    file_ = open(filename, 'wb')
    file_.write(data)
    file_.close()
    print("URL list downloaded...")
except TimeoutError:
    print("Timeout.Will try again in 30 minutes")
    time.sleep(1800)
    os.system('api_test.py')
except urllib.error as e:
    print(e)



with open('usom_download.txt') as fh:
  url_var_ = fh.read().splitlines()
  
none_cats = []
categorized = 0
uncategorized = 0


for testurl in url_var_:

    #testurl='iclikoftesiparisalinir.com/wp-content/gallery/630CIKLXRL/com/Business)'

    url = proxysgurl+"/ContentFilter/TestUrl/"+testurl+"/"

    print (url)  #kaldırılacak

    http = urllib3.PoolManager()
    myHeaders = urllib3.util.make_headers(basic_auth=auth_user+':'+auth_passwd) #proxy view only user
    res=http.request('GET', url, headers=myHeaders)
    test=res.data.decode('utf-8')
    print(test)
    
    if "security threats" in test.lower():
        #print('Security Threat')
        categorized +=1
    elif 'security concerns' in test.lower():
        #print('Security Concerns')
        categorized +=1
    else:
        #print('not Found')
        uncategorized +=1
        none_cats.append(testurl)
        
print ('categorized =',categorized)
print ('uncategorized =',uncategorized)
#print (none_cats)

  

#---------son list oluşturma start
#url_var=["badsite1.com","donotenter.com"]
url_desc=",'Block this site.','"
enb="'true'"
json_dataset=[]
for jsonlist in none_cats:
    json_dataset.append((jsonlist, "USOM database.",True),)
    


df = pd.DataFrame(json_dataset,columns = ['url','description','enabled'])


# Convert Pandas DataFrame To JSON Using orient = 'records' 
df2 = df.to_json(orient = 'records')
df.to_json(r'export_dataframe.txt',orient='records')
#---------son list oluşturma end

#---------json reformat start
f = open('export_dataframe.txt', 'r')
file_contents = f.read()
f.close()

new_str = file_contents.replace('[', '{"content": {"urls": [', 1)
new_str2 = new_str.replace(']', '],"advancedSettings": {"includeServerCertificateCpl": True,"includeSubnetCpl": True,"trigger": "URL","serverUrl": False}},"contentType": "URL_LIST","schemaVersion": "1.0","changeDescription": "Updated deny list with new entries"}', 1)
new_str3 =new_str2.replace('\/', '/')
#---------json reformat end


#-------script file create start
f = open('export_dataframe.txt', 'r')
file_content_sf = f.read()
f.close()

sf_str = file_content_sf.replace('[', '{"content": {"urls": [', 1)
sf_str2 = sf_str.replace(']', '],"advancedSettings": {"includeServerCertificateCpl": True,"includeSubnetCpl": True,"trigger": "URL","serverUrl": False}},"contentType": "URL_LIST","schemaVersion": "1.0","changeDescription": "Updated deny list with new entries"}', 1)
sf_str3 = sf_str2.replace('\/', '/')
sf_str4 = sf_str3.replace('true', 'True')

sf_str5='#created via python\nimport json\nimport requests\nimport urllib\nimport urllib3\nurllib3.disable_warnings()\nApiUrl="'+McUpurl+'"\nsf_str6 = '+sf_str4+'\npayload=json.dumps(sf_str6)\nheaders = {\n\t"Authorization": "Basic '+authid+'",\n\t"Content-Type": "application/json"\n}\nprint(payload)\nresponse = requests.request("POST", ApiUrl, headers=headers, data=payload, verify=False)\nprint(response)'
filename2 = "mc_api.py"
file_ = open(filename2, 'w')
file_.write(sf_str5)
file_.close()

#-----Run python file
import os 
os.system('python mc_api.py')

#---- install policy
install_url="https://"+MC_info+":8082/api/jobs/"+job_ID+"/run"

payload={}

response = requests.request("POST", install_url, headers={'Authorization': 'Basic '+authid+''}, data=payload, verify=False)

print(response.text)

#time check
import time

current_time = time.ctime()
print(current_time)
