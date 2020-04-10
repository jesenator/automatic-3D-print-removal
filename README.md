# automatic-3D-print-removal
     In response to the recent COVID-19 pandemic I 3D printed respirators and face shields to donate to local healthcare facilities in need. I worked to increase production of 3D printed respirators by writing a Python program to make my 3D printer automatically remove the mask when finished and then start the next one.
     For other smaller prints, it worked to simply have the gantry push the print off, but this respirator was stuck too well to the build plate for that to be possible. Instead, I developed a way for the printer to interlock the gantry with the nose piece and then effectively pry it off the build plate.
     With this setup, I can leave my printer to continuously produce masks without any need for human intervention (until the filament runs out). This means significantly more masks can be made
     
	I just past the name of the g code file I want to repeat and the enter how many times and if it should wait to cool, and then it saves a new file with a eddited name.
	It also makes the purge line move over by a few milimeters every iteration.
	To make it compative with a different 3D printer (I wrote it to work for an Ender 3), edit the variables at the begining of the code to match what you need. For exaple, copy and paste the purge line your slicer makes into the variable "line", and edit the "subgcode" to whatever you need to remove the prints.
	There are also some helpful features to note:
		By default the print head will go to the avg x value ((minx+maxx)/2) to knock the print off
		It tells you the print time and filament used
		It renames the file and adds multiprint(n).gcode where n is the number of iterations
		It will report an error if the print is iterated too many times and the purge line overlaps with the print
		
