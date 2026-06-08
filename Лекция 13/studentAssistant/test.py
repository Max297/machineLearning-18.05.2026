passMin=50
passGood=70
passPerfect=90

students ={
    "12351261251":{
        "name":"Иванов Иван Иванович",
        "group":"ТРУ-26",
        "grades":{
            "Математика":[5,1,2,6,1,10,4,8],
            "История":[2,1,7,2,5,2,10,2,2,1],
            "Английский":[1,2,7,2,1,5]
        }
    },
    "51351261851":{
        "name":"Петров Петр Петрович",
        "group":"ТРУ-26",
        "grades":{
            "Математика":[9,3,2,6,1,10,4,8],
            "История":[2,1,7,7,5,2,10,2,5,1],
            "Английский":[1,2,1,5]
        }
    }
}

def calculate_gpa(student:str, subject:str="")-> str:
    """"
    Ресурс для получения студентом информации о своих баллах по предметам.
    Параметры: номер зачетки студента и предмет, если предмет не указан, то получает информацию по всем.
    """
    if student in students:
        if (subject != ""):
            if(subject in students[student]["grades"]):
                studentResultArr = students[student]["grades"][subject]
                total = str(sum(studentResultArr))
                return "Студент имеет "+ total + " баллов по предмету: "+subject

            else:
                return "У студента нет баллов по данному предмету"
        else:
            allSubjects = students[student]["grades"]
            message=""
            for subject, points in allSubjects.items():
                total = str(sum(points))
                message = message + " сумма баллов по предмету "+ subject +" :"+total
            return  message
    else:
        return "Данного студента нет в нашей базе данных"

calculate_gpa("12351261251")
