######################################################################### variables
line=["G1 X0.1 Y20 Z0.3 F5000.0 ; Move to start position\nG1 X0.1 Y200.0 Z0.3 F1500.0 E15 ; Draw the first line",
      "G1 X0.4 Y200.0 Z0.3 F5000.0 ; Move to side a little\nG1 X0.4 Y20 Z0.3 F1500.0 E30 ; Draw the second line"]
newLine=["",""]
subgcode=''';-----------------start of multiprint substitution-----------------
G1 X110.452134 Y220 F8000; Move to the back
G1 Z0 F8000; Lower

;no bed cool

G1 Z0.2 F8000; raise so not scratching the bed

;no Covid special removal

G1 Y0 F2400; remove print
G1 Y20 F8000; shake
G1 Y0 F8000; shake
G0 Y190;  move back
G0 Y1;  move forward to expose sd card slot

M300 S3520 P200 ; A7
M300 S4698.63 P200 ; D8
M300 S5274.04 P200 ; E8
M300 S6271.93 P200 ; G8
;-------------------------------------------------------------------------------'''
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
G1 X235 Y150 F10000
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


'''
reset:

G1 Z60 F10000

G1 X220 Y220 F8000; Move to the back


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
;M190 R40; wait for bed to reach exactly 40
M190 S0; set bed to 0
G4 S1; wait
'''

offset=1.6
#########################################################################inputs
coolTime=0
COVID="none"
filename=input("paste the filename of the gcode to be edited")
n=int(input("enter the number of objects needed"))
#coolTime=float(input("how long should the bed wait to cool down (minutes) "))
COVID=input("COVID mask removal sequence? (mask or shield or none)")
if(COVID=="mask"):
    print("note: ensure that the mask is in the correct spot with Y=27.5295, and the nose pointing in positive Y direction")
if(COVID=="shield"):
    print("note: ensure that the face shield is in the correct spot")

gcode = open(filename, "r+", 1)
originalCode=gcode.read()
newCode=originalCode.replace(toDelete, "")


linesx=.4+offset*(n-1)

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

minx=float(minx[6:-1])
maxx=float(maxx[6:-1])
maxy=float(maxy[6:-1])
avgx=round((minx+maxx)/2, 1)
subgcode=subgcode.replace("110.452134", str(avgx))

if(coolTime>0):
    bedCool=bedCool.replace("S1", ("S" + str(coolTime*60)))
    subgcode=subgcode.replace(";no bed cool", bedCool)
if(COVID=="mask"):
    subgcode=subgcode.replace(";no Covid special removal", maskSubgcode)
if(COVID=="shield"):
           subgcode=subgcode.replace(";no Covid special removal", shieldSubgcode)
     

maxObjects=round(((-.4+minx)/offset))
if(n>maxObjects):
    print("ERROR: the lines will overlap with the print. (they go to " + str(linesx) + ") Either print is too close to left edge, or it is iterated too many times")
    print("it will automatically set to the maximum possible objects")
    n=maxObjects

meters=float(meters[16:-2])*n

filename=filename.replace(".gcode", "") + "[x" + str(n) + "].gcode"
newgcode=open(filename, "w+")


gcode.seek(0,0)

for a in range(0, int(n)-1):
    code=originalCode
    newLine[0]=line[0].replace("X0.1", ("X" + str(round((0.1+offset*int(a+1)), 1)))) 
    newLine[1]=line[1].replace("X0.4", ("X" + str(round((0.4+offset*int(a+1)), 1))))

    code=code.replace(line[0], newLine[0])
    code=code.replace(line[1], newLine[1])

    if(a<n-2):
        code=code.replace(toDelete, "")
    
    newCode=newCode + subgcode + "\n;--------start of iteration number " + str(a+2) + "--------\n" + code
#print(newCode)
#newgcode.write(subgcode)
newgcode.write(newCode)


print("\nfilename: " + filename)
print("total time: " + str(round((int(time[6:])+30)*n/3600, 2)) + " hours")
print("total meters: " + str(round(meters, 2)))
print("total cost: $" + str(round(meters*.07, 2)))
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

files
    CE3_covid_mask(.6mm).gcode - messed up because layers delaminated when removing the print, so it didnt come all the way off
    CE3_mask(.6~.4~210-105).gcode - .4 layer heigh instead of .48


'''



