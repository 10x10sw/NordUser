# NordUser RefCard

![](samples/ns3_example.png?raw=true)

## What This Script Does
This Python script creates a program list "reference card" for Nord keyboards by transforming the
HTML Program List output from the Nord Sound Manager program.
The reference card is a grid based on page and program. 
For keyboards with more than one bank of sounds, a separate grid is produced for each bank. 
It works for the Electro 4, 6; Lead A1; Stage 2, 2EX, 3; and may work for other models as well.
This has been tested with the output of Nord Sound Manager 6.86 build 734_12 [OSX Intel].

## Why This Script
Some Nord keyboards have only a small multi-digit LED display; you cannot see the name of the program.
Nord Sound Manager will export a list of the program names, but it is a linear list and contains a lot of useless information. 
This list is not useful when you want to quickly find a preset sound based on its page and program location, nor is it attractive to look at. 
This script changes the list into a two-dimensional table (or tables) based on page and program, with a design that matches the look of the Nord keyboards. 

## What You Need

This script requires the HTML file generated by Nord Sound Manager.
You must hook up your Nord keyboard to Nord Sound Manager version 6.86 or newer,
and choose "Export Sound Lists…" from the "File" menu.
The Nord software will create several files. This script uses the "Program" file
(for example: "Nord Electro 4 Program 2016-11-02.html"). 

## Help
Here is the output of `python make_nord_refcard.py -h` :
```
usage: make_nord_refcard.py [-h] [-o OUTPUTFILE] [-r] [-R] [-t TITLE] [-v] [--eurostile] inputFile

Creates a Program Reference Card for Nord Keyboards.
This version of the script supports at minimum the following models:
   Electro 4, 6; Lead A1; Stage 2, 2EX, 3.

positional arguments:
  inputFile                   the input Nord Sound Manager Program HTML file

optional arguments:
  -h, --help                  show this help message and exit
  -o OUTPUTFILE, --outputFile OUTPUTFILE
                              the output HTML file
  -r, --reverse               print the program pages in reverse order (from high to low)
  -R, --rotate                rotate the program page rows and columns
  -t TITLE, --title TITLE     an optional title to print above each bank
  -v, --verbose               print the sample name(s) or organ model below the program name
  --eurostile                 use Eurostile Extd font for titles and banks
  ```


## Fonts
Nord appears to use Eurostile Extended for the titles on the front panel,
and Trebuchet MS for the control labels. This script will use those fonts if they
are available, but will fall back to Helvetica or Arial if they are not.
Since most users do not have Eurostile installed, by default the script will use
a stretched version of Helvetica or Arial for title and bank names.
Use the `--eurostile` argument if you have Eurostile Extended ("Eurostyle Extd") installed.

## Examples

To use the input file `ne4_input_program.html` and dump the programs,
as well as the detailed sample and organ model,
starting with page 32 at the top and page 1 at the bottom,
with the title "Electro 4D,"
into the output file `refcard.html` : 
```
python make_nord_refcard ne4_input_program.html -v -r --eurostile -t "Electro 4D" -o refcard.html
```
![](samples/ne4_example.png?raw=true)

To use the input file `ns2_input_program.html` and dump only the program names,
starting with page 1 at the top and page 20 at the bottom for each bank,
with the title "Nord Stage 2," 
into the output file `refcard.html`: 
```
python make_nord_refcard ns2_input_program.html --eurostile -t "Nord Stage 2" -o refcard.html
```
![](samples/ns2_example.png?raw=true)
