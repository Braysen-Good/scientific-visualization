# Scientific Visualization - Project 14
The goal for this project was to create a Jupyter widget which could interactively display the output of a  PhysiCell simulation.  This included the ability to move through the environment, color the objects in the environment, visualize the attributes of a selected cell through graphs, and create an animation of the simulation.
## Group Members
  * Braysen Goodwin
  * David Oliphant
  * Jared Scott
  
# PhysiCell Simulation Visualization
![Example Vizualization](/Images/viz.png "")

# Setting Up The Enviornment

## Python Dependecies:
  * Python 3.0 or later
  * vtk
  * ipywidgets
  * numpy
  * asyncio
  * matplotlib 
  * ipycanvas
## Other  Dependecies:
  * Physicell (For Data) 
  * Node.js (Version 12 or Greater) 

## Data
Place the PhysiCell data files (.mat,.xml,.svg) into an output folder which resides within the working directory of your interactive notebook.<br>
Within the `Environment.ipynb` file, adjust the path of the output folder. 
`env = viewSimulation('./<Path To Output>', width=800, height=800)`
Example File Structure

    .
    |
    PhysiCell
       -.
        |PhysiCell
        |System Files
        |
        |output            <---
        |Environment.ipnyb <---
    
# Using the Available Tools
Choose the desired tool from the tool selction menu.<br>
As well as the desired frame from within the data.<br>
![Tools](/Images/tools.PNG "")

## Move Tool
Clicking and dragging with the move tool will move the representation around the visualization space. 

## Zoom Tool 
Clicking and dragging with the zoom tool will zoom in and out.

## Rotate Tool 
Clicking and dragging with the rotate tool will rotate the representation.

## Select Tool 
Clicking on a specific cell will select it. The selected cell will be highlighted with white.<br>
The selected cell's information will be displayed at the bottom left corner of the visualization. 

## Generating Attribute Time Graphs 
Once the desired cell is selected, simply choose the attribute you would like to analyze from the available attibutes.<br>
![Tools](/Images/attributes.PNG "")

## Visibility
Use this menu to toggle which actors are visible within the render window.<br>
You may hold shift to select more than one.<br>
![Tools](/Images/visible.PNG "")

# Creating an Animation
Place and run the script `createAnimation.py` within the output folder (location of .svg data files).<br>
There will be a .mp4 file named `simVid.mp4` within the working directory.

# Examples - Play around with the tool
There is a notebook called `./Examples.ipynb` which shows how to use this tool. Play around and have fun with it.
