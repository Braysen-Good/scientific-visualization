# constants from the contant header file from Physicell `PhysiCell/core/PhysiCell_constants.h`

# currently recognized cell cycle models 
advanced_Ki67_cycle_model = 0
basic_Ki67_cycle_model = 1
flow_cytometry_cycle_model = 2
live_apoptotic_cycle_model = 3
total_cells_cycle_model = 4
live_cells_cycle_model = 5 
flow_cytometry_separated_cycle_model = 6 
cycling_quiescent_model = 7 

# currently recognized death models 
apoptosis_death_model = 100 
necrosis_death_model = 101 
autophagy_death_model = 102 

custom_cycle_model = 9999

# currently recognized cell cycle and death phases and cycle phases
Ki67_positive_premitotic = 0
Ki67_positive_postmitotic = 1
Ki67_positive = 2
Ki67_negative = 3
G0G1_phase = 4
G0_phase = 5
G1_phase = 6 
G1a_phase = 7 
G1b_phase = 8
G1c_phase = 9
S_phase = 10
G2M_phase = 11
G2_phase = 12
M_phase = 13
live = 14
	
G1pm_phase = 15
G1ps_phase = 16
	
cycling = 17
quiescent = 18
	
	
custom_phase = 9999

# death phases
apoptotic = 100
necrotic_swelling = 101
necrotic_lysed = 102
necrotic = 103
debris = 104


# -------------------------------------- package constants ------------------------------------

# actions
MOVE_ACTION = 'move'
ZOOM_ACTION = 'zoom'
SELECT_ACTION = 'select'
ROTATE_ACTION = 'rotate'

# views
VISIBLE_CELL = "cell"