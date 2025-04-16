from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.StlAPI import StlAPI_Writer
from OCC.Core.TCollection import TCollection_AsciiString
from OCC.Core.IFSelect import IFSelect_ReturnStatus

input_file = 'Flywheel.stp'  # Input STEP
output_file = 'Flywheel.stl'  # Output STL

try:
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(input_file)
    if status != IFSelect_ReturnStatus.IFSelect_RetDone:
        raise Exception(f"Error reading STEP file: {input_file}")

    step_reader.TransferRoots()
    num_shapes = step_reader.NbRootsForTransfer()
    print(f"Number of shapes: {num_shapes}")

    for i in range(num_shapes):
        shape = step_reader.Shape(i + 1)
        if shape.IsNull():
            print(f"Shape {i + 1} is null.")
        else:
            shape_name = shape.Name() if shape.Name() else "Unnamed"
            print(f"Shape {i + 1} name: {shape_name}")

    print("STEP File read successfully.")

    # Export to STL
    stl_writer = StlAPI_Writer()
    stl_writer.SetASCIIMode(True)
    stl_writer.Write(step_reader.Shape(1), output_file)
    print("STL file written successfully.")

except Exception as e:
    print(f"Error: {e}")
