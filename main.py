#Script - extractor de plan de actividades a Markdown

#get user data login from file
#the file coulb be contain only the user and password with and line break:
#   user
#   password
with open("data.user", "r") as f:
    data_user = f.readline()
    data_pass = f.readline()

#import libraries
import re
from os import remove
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

try:
    #set driver path
    service = webdriver.FirefoxService("geckodriver")

    #start firefox bot with driver
    d = webdriver.Firefox(service = service)
    d.get("https://uam.terna.net/") #get page

    #give user
    user = d.find_element(By.NAME, "username")
    user.send_keys(data_user)

    #give password
    password = d.find_element(By.NAME, "password")
    password.send_keys(data_pass)

    #button login
    btn_login = d.find_element(By.XPATH, "/html/body/header/nav/div/div[2]/form/button")
    btn_login.click()

    # ------------------------------ loggin succesx ------------------------------ #
    d.get("https://uam.terna.net/VerNotasLapso.php?mid=0")

    #download the page
    with open("index.html", "w") as f:
        f.write(d.page_source)
        
    d.quit()
    
    # ----------------------------- download success ----------------------------- #
    filehtml = open("index.html", "r") #open html data
    content = filehtml.read()
    filehtml.close()

    p = BeautifulSoup(content, "html.parser") #init library

    #subject names
    subjects = {}
    td = p.find_all("td", {"class":"table-sub-title"})

    #create template
    for x in td:
        x = re.sub(r".*?\s\dM[ABC]?\s", "", x.text.replace("\n", "")) #remove id code
        x = re.sub(r"\s+", " ", x).strip()
        
        subjects[x] = {"c1" : None, "c2" : None, "c3" : None} #define key with the subject name and a sub dict with lapses to fill
        
    keys_names = list(subjects.keys()) #save the subjects names
        
    #subjects content
    td = p.find_all("td", {"class":"text-left"})

    #in this point the loop searchs the subject content and make a format {date-content}
    i = 0
    for K in range(len(keys_names)):
        loop = True
        string = []
        temp_str = []
        
        while loop == True:
            t = td[i].text
            
            if len(t) > 40:
                date = re.search(r"\d{2}-\d{2}-\d{4}", t).group()
                
                t = re.split(r"\d{2}-\d{2}-\d{4}", t)[1]
                t = re.sub(r"\s+", " ", t).replace(" ,", ",").replace(",", ", ")
                temp_str.append(date + "-" + t + "\n")
            
            else:
                if re.search("C1. 1er Corte", t) or re.search("C2. 2do Corte", t):
                    string.append(temp_str)
                    temp_str = []
                
                if re.search("C3. 3er Corte", t):
                    string.append(temp_str)
                    loop = False
                
            i += 1
        
        subjects[keys_names[K]]["c1"] = string[0]
        subjects[keys_names[K]]["c2"] = string[1]
        subjects[keys_names[K]]["c3"] = string[2]
    
    #DONE UNTILL THIS PART, THE SUBJECTS AND ACTIVITIES WAS EXTRACTED AT THIS POINT
    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    lapses_names = {"c1": "1er Corte", "c2": "2do Corte", "c3": "3er Corte"}

    md_file = open("output.md", "w")

    for sub_name, corte in subjects.items():
        md_file.write(f'## <b style="color:pink">{sub_name}</b>\n')
        for corte, tema in corte.items():
            md_file.write(f"### **{lapses_names[corte]}**\n")
            for valu in tema:
                fecha = re.search(r"\d{2}-\d{2}-\d{4}", valu).group() 
                dia_semana = datetime.strptime(fecha, "%d-%m-%Y").weekday()
                
                title = f"- [ ] Evaluación ({day_names[dia_semana]} {re.sub(r"-", " - ", fecha)})\n"
                
                valu = f'    <p style="color: #888">[{re.sub(r"\d{2}-\d{2}-\d{4}-", "", valu).replace(" \n", "")}]</p>\n'
                md_file.write(title)
                md_file.write(valu)
            md_file.write("</br>\n")

    md_file.close()
    remove("index.html")

except Exception as e:
    print(e)
    d.quit()
