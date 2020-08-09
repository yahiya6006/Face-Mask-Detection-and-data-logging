# import the file
import msxlt

# Create a class object.
xl = msxlt.XLC()

# create() method is used to create a an XL document.
# First parameter input is the names of the coloums
# 2nd parameter input is the file name
# 3rd parameter input is the sheet name
# -----------------------here is an example--------------------------------
xl.create("Date,Time,Person Identified,Status", "test", "Face Mask Detection data")

# time_date() returns the current time and date when the function is called
time, date = xl.time_date()
print("Time =",time,"Date =",date)

# this is juat a tuple which i have created to represent how to update the excel sheet
person_data = ("Yahiya Mulla","Bill","Tony","KAYA")
for i in range(0,4):
    person = person_data[i]

    # Data to be stored needs to be arranged in the same order as the coloums were created.
    # All the input feilds should be seperated by a comma (,) as shown below..
    data = date+','+time+','+person+','+'Testing data'
    xl.updateData(data,"test")

# congratulations!!!!
