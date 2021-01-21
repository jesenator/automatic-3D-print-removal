package com.company;
import java.io.File;  // Import the File class
import java.io.FileNotFoundException;  // Import this class to handle errors
import java.util.Scanner; // Import the Scanner class to read text files
import java.io.IOException;  // Import the IOException class to handle errors
import java.io.FileWriter;   // Import the FileWriter class

// additional info:
/*
You will need 2 additional files:

a file titled "subGcode.txt" that contains the gcode that will be inserted between the prints to knock the print off
I use this for my ender 3:


        ;-----------------start of multiprint substitution-----------------
        G1 X117.5 Y210 F8000; Move to the back (change the 117.5 to x coordinate when the nozel is centered on the bed)
        G1 Z0 F8000; Lower so th nozel is pressed into bed and filament cannot leak out
        ;no bed cool
        G1 Z0.8 F8000; raise so not scratching the bed
        ;no special removal
        G1 Y0 F2400; remove print
        G1 Y20 F8000; shake
        G1 Y0 F8000; shake
        G0 Y190;  move back and dump print
        G0 Y1;  move forward to expose sd card slot
        ;-------------------------------------------------------------------------------


a file titled "toDelete.txt" the contains the gcode that that turns off the bed and hotend
for the ender 3 on cura that is this:

        G1 X0 Y235 ;Present print
        M106 S0 ;Turn-off fan
        M104 S0 ;Turn-off hotend
        M140 S0 ;Turn-off bed

        M84 X Y E ;Disable all steppers but Z
        M82 ;absolute extrusion mode
        M104 S0


 */

public class Main {

    public static String type;
    public static String fileName;
    public static String filePath = "C:\\Users\\jesse\\Desktop\\MultiprintFiles\\"; // file path to where to the gcode is going to be
    public static String pauseGcode = "M140 S0; cool bed\nG4 S300; wait 5 minutes\n";// edit to change how much time it waits for the bed to cool
    public static int numOfEachObject;
    public static int fileNum;
    public static String originalGcodes[];
    public static String newGcode;
    public static String newName;
    public static String oldPurgeLineGcode = "G1 X0.1 ; X start position\n";
    public static String newPurgeLineGcode = "G1 X%f ; X start position\n";

    public static boolean pause = false;
    public static double perModelHours;
    //prefab files
    public static String toDelete;
    public static String subGcode;


    public static void main(String[] args) {
        getInputs(); // enter all required numbers and file names
        readFiles(); // reads the files
        editSubGcode(); // add the required gcode to the subGcode
        System.out.println("processing...");
        repeatGcode(); // build the new gcode by repeating the gcode and adding the subGcode
        writeFile(newName, newGcode); // write to a new file with the new gcode and the new name
        displaySettings(); // print the settings used
    }

    public static void repeatGcode() {
        String addGcode;
        double purgeOffset = 2;
        double newPurgeStart = 0.1-purgeOffset;
//        newGcode = originalGcodes[0].replace(toDelete, ";removed ending gcode\n");
        for(int i = 0; i< numOfEachObject; i++) {
            for(int j=0; j<fileNum; j++) {
                if(i==0 && j==0)
                    addGcode = originalGcodes[0].replace(toDelete, ";removed ending gcode\n\n"); // for the first section
                else if (i == numOfEachObject -1 && j == fileNum-1)
                    addGcode = subGcode + originalGcodes[j];
                else
                    addGcode = subGcode + originalGcodes[j].replace(toDelete, ";removed ending gcode\n\n"); // for the last section

                newPurgeStart += purgeOffset;
                String temp = String.format(newPurgeLineGcode, newPurgeStart);
//                System.out.println("\n" + temp);
                addGcode = addGcode.replace(oldPurgeLineGcode, temp);

                newGcode += addGcode;
            }
        }
    }
    public static void getInputs() {
        //comment or comment out the relative print
        Scanner input = new Scanner(System.in);
        String temp;
        temp="5";
        //defaults
        fileNum = 1;
        numOfEachObject = 5;
        fileName = "compliant clip test v4.gcode";

//        System.out.print("Enter the number of distinct files to print: ");
//        fileNum = input.nextInt();


        System.out.print("Enter the number of each object needed: ");
        numOfEachObject = input.nextInt();

        Scanner input2 = new Scanner(System.in);

        if(fileNum>1) {
            System.out.println("The files need to be numbered 0 through " + (fileNum - 1) + " in the order they are to be printed.");
            System.out.print("\nEnter the name of the folder they are in: ");
            fileName = input2.nextLine();
            newName = filePath + fileName + "(x" + fileNum + "x" + numOfEachObject + ").gcode";
            filePath += fileName + "\\";
        }
        else if(fileNum==1) {
            System.out.print("Enter file name (with .gcode): ");
            fileName = input2.nextLine();
            newName = filePath + fileName.replace(".gcode", "") + "(x" + numOfEachObject + ").gcode";
            filePath += fileName;
        }
        originalGcodes = new String[fileNum];
        System.out.print("Do you want their to be a 2 minute wait before removal (optimal for glass beds) (y or n): ");
        temp = input.next();
        if(temp.compareToIgnoreCase("y")==0)
            pause = true;

//        System.out.print("Enter the time for one (in hours): ");
//        perModelHours = input.nextDouble();


//        System.out.print("\nEnter multiprint type: ");
//        type = input.nextLine();
    }
    public static void editSubGcode() {
        if(pause) {
            subGcode=subGcode.replace(";no bed cool", pauseGcode);
        }

    }
    public static void readFiles() {
        String tempPath;
        String prefabPath = "C:\\Users\\jesse\\IdeaProjects\\Multiprint\\src\\prefabText\\";
        if(fileNum==1) {
            originalGcodes[0] = readFile(filePath);
        }
        else {
            for (int i = 0; i < fileNum; i++) {
                tempPath = filePath + i + ".gcode";
                System.out.println(tempPath);
                originalGcodes[i] = readFile(tempPath);
            }
        }
        toDelete = readFile(prefabPath + "toDelete.txt");
        subGcode = readFile(prefabPath + "subGcode.txt");

    }
    public static String readFile(String fileName) {
        String data;
        String file = "";
        try {
            File myObj = new File(fileName);
            Scanner myReader = new Scanner(myObj);
            while (myReader.hasNextLine()) {
                data = myReader.nextLine();
                file += data + "\n";
            }
            myReader.close();
        } catch (FileNotFoundException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }

        return file;

    }
    public static void writeFile(String fileName, String fileText) {
        try {
            FileWriter myWriter = new FileWriter(fileName);
            myWriter.write(fileText);
            myWriter.close();
            System.out.println("Successfully wrote to the file.");
        } catch (IOException e) {
            System.out.println("An error occurred.");
            e.printStackTrace();
        }
//        try {
//            File myObj = new File(fileName);
//            if (myObj.createNewFile()) {
//                System.out.println("File created: " + myObj.getName());
//            } else {
//                System.out.println("File already exists.");
//            }
//        } catch (IOException e) {
//            System.out.println("An error occurred.");
//            e.printStackTrace();
//        }
    }
    public static void displaySettings() {
        int totalObjects = fileNum * numOfEachObject;
        System.out.println("\npause: " + pause);
        System.out.println("filename and location: " + newName);
        System.out.println("total objects printed: " + totalObjects);
        System.out.println("total time (in hours): " + perModelHours * totalObjects);
//        System.out.println("");
    }

    //Note: the last M104 S0 isn't there when the print is one layer or really small

}
