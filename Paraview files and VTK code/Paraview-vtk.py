

  # Need to specify full path/filename
  if 'win32' in sys.platform:   # running on Windows
    dir = os.environ['USERPROFILE'] + '/Downloads/'
  else:   # Linux or darwin/OSX
    dir = os.environ['HOME'] + '/Downloads/'

  if (os.getenv('PHYSICELL_DATA') != None):
    dir = os.getenv('PHYSICELL_DATA') + '/'
    print 'Using PHYSICELL_DATA as data directory. '
    #print 'Provide the "dir" path in the Reader script.'

#  dir = '/Users/specify-full-path-to-the-data/'
  print 'dir=',dir  
  fname = "output%08d_cells_physicell.mat" % iframe
  full_fname = dir + fname
  print 'full_fname=',full_fname

  if (os.path.isfile(full_fname) == False):
    print '\n==== WARNING ===='
    print 'Input file ',full_fname, ' does not exist.'
    # let's just generate an error which will popup the Output Msgs

  scipy.io.loadmat(full_fname, cells_dict)
  val = cells_dict['cells']

  # Get a vtk.PolyData object for the output
  pdo = self.GetPolyDataOutput()

  # Get number of cells
  num_cells_possible = val.shape[1]
  print "num_cells_possible =",num_cells_possible

  # Create points (cells' centers)
  newPts = vtk.vtkPoints()

  # We will create two scalar fields:
  #   cell_color_ID = integers that get mapped to colors (for cell types)
  #   cell_diam = floating point values of cell diameters
  cell_color_ID = vtk.vtkIntArray()
  cell_diam = vtk.vtkFloatArray()
  cell_color_ID.SetName('cell_color_ID')
  cell_diam.SetName('cell_diameter')


  #kdx=6
  #if (kdx == 5):
#  scalars.SetName('cell_type')
  #elif (kdx == 6):
  #  scalars.SetName('cycle_model')
  #elif (kdx == 7):
  #  scalars.SetName('current_phase')

  # This is a temporary hack to correct
  # for a shortcoming in ParaView's OSPRay
  # sphere scaling. Basically, we need to
  # move all cells closer to the origin.
  first_pass = False
  if (first_pass):
    maxDist = 0.0
  else:
    maxDist = 4.0  # ~3.90

  num_cells = 0
  for idx in range(0, num_cells_possible):   # loop over all (possible) cells
    # rf. PhysiCell User Guide for interpretation of these array indices
    x = val[1,idx]
    y = -val[2,idx]  # invert Y (points down)
    z = val[3,idx]
    if (math.fabs(x) > 1000):
      print idx," skip x =", x
      continue
    elif (math.fabs(y) > 1000):
      print idx," skip y =", y
      continue
    elif (math.fabs(z) > 1000):
      print idx," skip z =", z
      continue

    # If reading a new .mat data file
    # of unknown spatial size, do this:
    if (first_pass):
      dist = math.sqrt(x*x + y*y + z*z)
      if dist > maxDist:
        maxDist = dist

    # insert new (only if valid) point
    # temporary hack: move cell centers closer to origin
    newPts.InsertPoint(num_cells, x/maxDist,y/maxDist,z/maxDist)
    num_cells += 1

    # The following lines assign an integer to represent
    # a color, defined in a Color Map.
    sval = 0   # immune cells are black?
    if val[5,idx] == 1:  # [5]=cell_type
      sval = 1   # lime green
    if (val[6,idx] == 6) or (val[6,idx] == 7):
      sval = 0
    if val[7,idx] == 100:  # [7]=current_phase
      sval = 3   # apoptotic: red
    if val[7,idx] > 100 and val[7,idx] < 104:
      sval = 2   # necrotic: brownish

    cell_color_ID.InsertNextValue(sval)

    # This is where we create another scalar field that
    # will determine how cells (spheres) are scaled.
    # V=(4/3)pi*r^3 -> r^3 = v*0.75/pi
    diam = (val[4,idx]*0.2387)**0.333 * 2.0
    cell_diam.InsertNextValue(diam)

  # If doing a 1st-pass to determine max distance
  # of a cell from the origin:
  #print 'maxDist = ',maxDist

  # Add the points and the scalar arrays to the vtkPolyData object.
  pdo.SetPoints(newPts)
  pdo.GetPointData().AddArray(cell_color_ID)
  pdo.GetPointData().AddArray(cell_diam)

  verts = vtk.vtkCellArray()
  print "num_cells =",num_cells

  for idx in range(0, num_cells):
    verts.InsertNextCell(1)
    verts.InsertCellPoint(idx)

  pdo.SetVerts(verts)

for iframe in [3696]:    # or, "in range(start, end+1, step):"
  render_cells(iframe)

# Need to manually append following to the saved (Python) state
#WriteImage(png_fname + ".png")