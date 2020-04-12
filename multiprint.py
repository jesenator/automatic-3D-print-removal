######################################################################### variable declerations
line=["G1 X0.1 Y20 Z0.3 F5000.0 ; Move to start position\nG1 X0.1 Y200.0 Z0.3 F1500.0 E15 ; Draw the first line",
      "G1 X0.4 Y200.0 Z0.3 F5000.0 ; Move to side a little\nG1 X0.4 Y20 Z0.3 F1500.0 E30 ; Draw the second line"]

newLine=["",""]

subgcode=''';-----------------start of multiprint substitution-----------------
G1 X110.452134 Y220 F8000; Move to the back (note that the avg x value is substituted)
G1 Z0 F8000; Lower so nozel is pressed into bed and filament cannot leak out

;no bed cool

G1 Z0.2 F8000; raise so not scratching the bed

;no special removal

G1 Y0 F2400; remove print
G1 Y20 F8000; shake
G1 Y0 F8000; shake
G0 Y190;  move back
G0 Y1;  move forward to expose sd card slot
;-------------------------------------------------------------------------------
'''

maskSubgcode='''
;----COVID mask removal substitution------
G1 Z4 F8000
G1 X220; extruder to the right and out of the way
G1 Y135; lining nose of the mask up with the extrusion
G1 Z10 F100; lift mask up
G1 Z4 F1000
G1 Y134 F100
G1 Z10
G1 Z16 Y132
G1 Z20 Y 128
G1 Y140 F8000; go backward
G1 Z4; go down
;-----------------------------------------
'''

shieldSubgcode='''
;--------COVID face shield removal substition-------------
G1 Z20 F10000
G1 X235 Y150 
G1 Z.2
G1 X230 F1000
G1 X231
G1 Z20 F10000
G1 X0
G1 Z.2
G1 X5 F1000
G1 X4
G1 Z20 F10000
G1 X115
G1 Z.2
G1 Y0 F1000
;------------------------------------------------
'''

toDelete='''
G1 X0 Y235 ;Present print
M106 S0 ;Turn-off fan
M104 S0 ;Turn-off hotend
M140 S0 ;Turn-off bed

M84 X Y E ;Disable all steppers but Z

M82 ;absolute extrusion mode
M104 S0
'''

bedCool='''
M190 S0; set bed to 0
G4 S1; wait
'''

manual=''';-----------------start of multiprint manual substitution-----------------
M300 S440 P200 ; Make Print Completed Tones
M300 S660 P250
M300 S880 P300

G1 X0 Y235 ;Present print

M0 S10 "remove print then click to continue"

M106 S0 ;Turn-off fan
M104 S0 ;Turn-off hotend
M140 S0 ;Turn-off bed

M0 remove print then click to continue

M140 S{material_bed_temperature_layer_0} ; start preheating the bed
M104 S{material_print_temperature_layer_0} T0; start preheating hotend
M190 S{material_bed_temperature_layer_0} ; heat to Cura Bed setting 
M109 S{material_print_temperature_layer_0} T0 ; heat to Cura Hotend
;---------------------------------------------------------------------------
'''

offset=1.6
fileLocation="C:/Users/lgilb/AppData/Local/Programs/Python/Python38/G code/"
######################################################################### user inputs
#default values
filename="CE3_NIH visor(x2~1~.48).gcode"
n=10
coolTime=0
special="manual"
#the file needs to be in the specified folder and not be labled with .gcode, but when typing the name it should have the .gcode

#uncomment the follwing 4 lines to be able to enter their valus

#filename=input("paste the filename of the gcode to be edited (make sure it is in the g code folder")
#special=input("special removal sequence? (mask, shield, manual, or none)")
if(special!="mask" and special!="shield" and special!="manual" and special!="none"):
    special="none"
if(special!="manual"):
    print("")
    #n=int(input("enter the number of objects needed"))
    #coolTime=float(input("how long should the bed wait to cool down (minutes) "))


#read file
gcode = open((fileLocation+filename), "r+", 1)
originalCode=gcode.read()
newCode=originalCode.replace(toDelete, "")


#read values from g code such as filament used, time, and min and max location values
gcode.seek(0,0)
gcode.readline()
time=gcode.readline()

meters=gcode.readline()

gcode.readline()
minx=gcode.readline()
gcode.readline()
gcode.readline()
maxx=gcode.readline()
maxy=gcode.readline()

meters=float(meters[16:-2])
minx=float(minx[6:-1])
maxx=float(maxx[6:-1])
maxy=float(maxy[6:-1])
avgx=round((minx+maxx)/2, 1)
subgcode=subgcode.replace("110.452134", str(avgx))

#adding in more g code to the subtitution for more features
#like a special removal sequence for the COVID-19 respirators and face shields
#which have too much surface area to be jsut pushed off
if(coolTime>0):
    bedCool=bedCool.replace("S1", ("S" + str(coolTime*60)))
    subgcode=subgcode.replace(";no bed cool", bedCool)
if(special=="mask"):
    print("note: ensure that the mask is in the correct spot with Y=27.5295, and the nose pointing in positive Y direction")
    subgcode=subgcode.replace(";no special removal", maskSubgcode)
if(special=="shield"):
    print("note: ensure that the face shield is in the correct spot Y=28 X=-3")
    subgcode=subgcode.replace(";no special removal", shieldSubgcode)
if(special=="manual"):
    print("the the printer will stay heated for 5 minutes after finishing for you to remove the print, then press the knob twice to print the next (don't forget the purge line)")
    subgcode=manual

#figuring out how far the purge lines will go based on how many times it is iterated
if(special!="manual"):
    linesx=.4+offset*(n-1)   
    maxObjects=round(((-.4+minx)/offset))
    if(n>maxObjects):
        print("ERROR: the lines will overlap with the print. (they go to " + str(linesx) + ") Either print is too close to left edge, or it is iterated too many times")
        print("it will automatically set to the maximum possible objects")
        n=maxObjects
    filename=filename.replace(".gcode", "") + "[x" + str(n) + "].gcode"
else:
    filename=filename.replace(".gcode", "") + "[manual].gcode"
    newgcode=open((fileLocation+filename), "w+")
    n=round(330/meters)


gcode.seek(0,0)

#building new g-code
for a in range(0, int(n)-1):
    print(a)
    code=originalCode
    if(special!="manual"):
        #replace x values of the purgeline over by an offset for each iteration
        newLine[0]=line[0].replace("X0.1", ("X" + str(round((0.1+offset*int(a+1)), 1)))) 
        newLine[1]=line[1].replace("X0.4", ("X" + str(round((0.4+offset*int(a+1)), 1))))
        code=code.replace(line[0], newLine[0])
        code=code.replace(line[1], newLine[1])

    if(a<n-2): #for each itiration except the last, remove the g code that tells the printer to turn off the bed and hot end
        code=code.replace(toDelete, "")
    
    newCode=newCode + subgcode + "\n;--------start of iteration number " + str(a+2) + "--------\n" + code

#write new g-code to the
#print(newCode)
newgcode.write(newCode)

#print info
print("\nfilename: " + filename)
if(special!="manual"):
    print("total time: " + str(round((int(time[6:])+30)*n/3600, 2)) + " hours")
    print("total meters: " + str(round(meters*n, 2)))
    print("total cost: $" + str(round(meters*n*.07, 2)))
    print("avg x: " + str(avgx))
    print("maximum object that can be printed: " + str(maxObjects))


'''
Notes:
integrate script into Cura?
add more post processing funcitons
    -ability to alternate printing of multiple files
    -some way to get prints off the build plate easier and reduce damage to gantry
    -reduce chance of failure
    -use it to print a lot of something to test it
things to improve removal
    
things to fix
    -for some reason, the empty_Multiprint(n).gcode is empty when n is <=4 i have no idea why.
        also, the newgcode write isn't working how i expect it to
    -after printing in the same place repeatedly, the print sticks much better, which makes it harder to remove
        -have the mask be print in different places
    -make the notes actually work
files
    CE3_covid_mask(.6mm).gcode - messed up because layers delaminated when removing the print, so it didnt come all the way off
    CE3_mask(.6~.4~210-105).gcode - .4 layer heigh instead of .48
'''

