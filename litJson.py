import json

fichier = "config.json"

with open(fichier) as json_data:
    data_dict = json.load(json_data)
    #print(data_dict)
    
for i in data_dict:
        if i["quizzName"] == 'quizz2':
            print("\n" +str(i) + "\n")
            print(i["quizzTable"])
            print(i["questions"])
            print(i["questions"][1])
            