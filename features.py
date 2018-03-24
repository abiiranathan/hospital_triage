from dateutil.relativedelta import relativedelta
from datetime import datetime

def compute_age_from_dates(dob, deceased=False, dod=""):
    today = datetime.today().date()
    if dob:
        start = datetime.strptime(str(dob), '%Y-%m-%d')
        end = datetime.strptime(str(today),'%Y-%m-%d')
        if deceased:
            end = datetime.strptime(
                        str(dod), '%Y-%m-%d %H:%M')

        rdelta = relativedelta(end, start)

        years = rdelta.years
        months= rdelta.months
        days= rdelta.days

        if months==0 and days==0 and years !=0:
            age = str(years) + "yr"
        elif years==0 and days==0 and months !=0:
            age = str(months) + 'm'
        elif years==0 and months==0 and days !=0:
            age = str(days) + 'd'
        elif  years !=0 and months !=0 and days ==0:
             age = str(years) + "yr " + str(months) + "m"
        elif years !=0 and months ==0 and int(days) !=0:
            age = str(years) + "yr " + str(days) + 'd'
        elif years ==0 and months !=0 and days !=0:
            age = str(months) + "m " + str(days) + 'd'
        elif years !=0 and months !=0 and int(days)!=0:
            age = str(years) + "yr " +str(months) + 'm ' + str(days) + 'd'
        elif years==0 and months==0 and days==0:
            age= "New born"
        else:
            age="Unable to compute age"

        return age

if __name__ == '__main__':
    print(compute_age_from_dates("2018-3-9"))