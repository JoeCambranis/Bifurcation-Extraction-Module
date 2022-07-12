import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# bifurc
#

class bifurc(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "bifurc"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Joeana Cambranis"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
This is a small module to obtain the bifurcations out of a centerline curve (markups). 
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
"""

    # Additional initialization step after application startup is complete
    slicer.app.connect("startupCompleted()", registerSampleData)

#
# Register sample data sets in Sample Data module
#

def registerSampleData():
  """
  Add data sets to Sample Data module.
  """
  # It is always recommended to provide sample data for users to make it easy to try the module,
  # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

  import SampleData
  iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

  # To ensure that the source code repository remains small (can be downloaded and installed quickly)
  # it is recommended to store data sets that are larger than a few MB in a Github release.

  # bifurc1
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='bifurc',
    sampleName='bifurc1',
    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    thumbnailFileName=os.path.join(iconsPath, 'bifurc1.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
    fileNames='bifurc1.nrrd',
    # Checksum to ensure file integrity. Can be computed by this command:
    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    checksums = 'SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
    # This node name will be used when the data set is loaded
    nodeNames='bifurc1'
  )

  # bifurc2
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='bifurc',
    sampleName='bifurc2',
    thumbnailFileName=os.path.join(iconsPath, 'bifurc2.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
    fileNames='bifurc2.nrrd',
    checksums = 'SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
    # This node name will be used when the data set is loaded
    nodeNames='bifurc2'
  )

#
# bifurcWidget
#

class bifurcWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False
    slicer.mymod = self
    self.startPos = None
    self.rows = 0
    self.columns = 0
    self.tableNode = None
    self.cont = 0
    self.new = 0
    self.endPos = None
    self.sPosSplit = 0
    self.ePosSplit = 0
    self.startPos2 = 0
    self.endPos0 = 0
    self.endPos1 = 0
    self.endPos2 = 0
    self.bifurcationPoints = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode')
    self.bifurcationPoints.CreateDefaultDisplayNodes()
    self.bifurcationPoints.SetName('Bifurcations_1')
    self.displayNode = self.bifurcationPoints.GetDisplayNode()
    self.displayNode.SetGlyphScale(2)
    self.displayNode.SetSelectedColor(1,0,0)

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)
    
    # This sets the view being used to the red view only -- it works
    slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalWidescreenView)
    
    #This defines which type of button you are using 
    self.usContainer = ctk.ctkCollapsibleButton()
    #This is what the button will say 
    self.usContainer.text = "Centerline Information"
    #Thiss actually creates that button
    self.layout.addWidget(self.usContainer)
    #This creates a variable that describes layout within this collapsible button 
    self.usLayout = qt.QFormLayout(self.usContainer)
    
    #Declare the server IP and server port
         
    # Combobox for image selection
    self.tableSelector = slicer.qMRMLNodeComboBox()
    self.tableSelector.nodeTypes = ["vtkMRMLTableNode"]
    self.tableSelector.selectNodeUponCreation = True
    # self.imageSelector.addEnabled = False
    # self.imageSelector.removeEnabled = False
    # self.imageSelector.noneEnabled = True
    # self.imageSelector.showHidden = False
    # self.imageSelector.showChildNodeTypes = False
    self.tableSelector.setMRMLScene( slicer.mrmlScene )
    self.tableSelector.setToolTip( "Pick the image to be used." )
    self.usLayout.addRow("US Volume: ", self.tableSelector)
       
    #This is a push button 
    self.applyButton = qt.QPushButton()
    self.applyButton.setDefault(False)
    #This button says connect 
    self.applyButton.text = "search for points"
    #help tooltip that explains the funciton 
    self.applyButton.toolTip = "Search for the bifurcation of the Centerline Curve"
    self.usLayout.addWidget(self.applyButton)
    
    #This is a push button 
    self.newButton = qt.QPushButton()
    self.newButton.setDefault(False)
    #This button says connect 
    self.newButton.text = "New Bifurcations"
    #help tooltip that explains the funciton 
    self.newButton.toolTip = "Clean data for new search"
    #adds the widget to the layout 
    if slicer.mrmlScene.GetNodesByClass("vtkMRMLSequenceNode").GetNumberOfItems() == 0:
      self.usLayout.addWidget(self.newButton)
    
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.newButton.connect('clicked(bool)', self.onNewClicked)


  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    # self.setParameterNode(self.logic.getParameterNode())

    # # Select default input nodes if nothing is selected yet to save a few clicks for the user
    # if not self._parameterNode.GetNodeReference("InputVolume"):
      # firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
      # if firstVolumeNode:
        # self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    # if inputParameterNode:
      # self.logic.setDefaultParameters(inputParameterNode)

    # # Unobserve previously selected parameter node and add an observer to the newly selected.
    # # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # # those are reflected immediately in the GUI.
    # if self._parameterNode is not None:
      # self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    # self._parameterNode = inputParameterNode
    # if self._parameterNode is not None:
      # self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # # Initial GUI update
    # self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # Update node selectors and sliders
    self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
    self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    self.ui.invertedOutputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolumeInverse"))
    self.ui.imageThresholdSliderWidget.value = float(self._parameterNode.GetParameter("Threshold"))
    self.ui.invertOutputCheckBox.checked = (self._parameterNode.GetParameter("Invert") == "true")

    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetNodeReference("OutputVolume"):
      self.ui.applyButton.toolTip = "Search for bifurcations"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input and output volume nodes"
      self.ui.applyButton.enabled = False

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
    self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
    self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")
    self._parameterNode.SetNodeReferenceID("OutputVolumeInverse", self.ui.invertedOutputSelector.currentNodeID)

    self._parameterNode.EndModify(wasModified) 
    
  def onApplyButton(self): #working good
  
    self.tableNode = self.tableSelector.currentNode()
    self.rows = self.tableNode.GetNumberOfRows()
    self.columns = self.tableNode.GetNumberOfColumns()
    print(self.rows)
    print(self.columns)
    print("YATA")    
    if self.new == 0:
     self.new = 1
     print('US bifurcations working')
     for i in range (0,self.rows):
       self.cont = self.cont + 1
       if self.cont == self.rows:
        #print("Start Point (final) = ",0, (self.columns -1))
        #print("End Point (final) = ", i, self.columns)
        self.startPos = self.tableNode.GetCellText(0, (self.columns -2)) #get next StartPointPosition
        self.endPos = self.tableNode.GetCellText(i,(self.columns-1)) #get the EndPointPosition        
        print("Start Position (1st):", self.startPos)
        print("End Point (last):", self.endPos)
        if self.startPos == self.endPos:
         print("BIFURCATION FOUND!")
         self.ePosSplit = self.endPos.split()
         print("End Point (split):", self.ePosSplit)  
         self.endPos0 = float(self.ePosSplit[0])    
         self.endPos1 = float(self.ePosSplit[1]) 
         self.endPos2 = float(self.ePosSplit[2]) 
         print("End Point (0):", self.endPos0)  
         print("End Point (1):", self.endPos1)
         print("End Point (2):", self.endPos2)
         self.bifurcationPoints = slicer.modules.markups.logic().AddFiducial(self.endPos0, self.endPos1, self.endPos2)
       elif self.cont != self.rows:
        #print("contador=", self.cont)
        self.startPos = self.tableNode.GetCellText((i + 1), (self.columns -2)) #get next StartPointPosition
        self.endPos = self.tableNode.GetCellText(i,(self.columns -1)) #get the EndPointPosition
        print("Start Position:", self.startPos)
        print("End Point:", self.endPos)
        if self.startPos == self.endPos:
         print("BIFURCATION FOUND!")
         self.ePosSplit = self.endPos.split()
         print("End Point (split):", self.ePosSplit)  
         self.endPos0 = float(self.ePosSplit[0])    
         self.endPos1 = float(self.ePosSplit[1]) 
         self.endPos2 = float(self.ePosSplit[2]) 
         print("End Point (0):", self.endPos0)  
         print("End Point (1):", self.endPos1)
         print("End Point (2):", self.endPos2)
         self.bifurcationPoints = slicer.modules.markups.logic().AddFiducial(self.endPos0, self.endPos1, self.endPos2)
     print("end of bifurcation localization #1")
    
    elif self.new == 1:
     self.new = 0
     print('US bifurcations working')
     for i in range (0,self.rows):
       self.cont = self.cont + 1
       if self.cont == self.rows:
        #print("Start Point (final) = ",0, (self.columns -1))
        #print("End Point (final) = ", i, self.columns)
        self.startPos = self.tableNode.GetCellText(0, (self.columns -2)) #get next StartPointPosition
        self.endPos = self.tableNode.GetCellText(i,(self.columns-1)) #get the EndPointPosition        
        print("Start Position (1st):", self.startPos)
        print("End Point (last):", self.endPos)
        if self.startPos == self.endPos:
         print("BIFURCATION FOUND!")
         self.ePosSplit = self.endPos.split()
         print("End Point (split):", self.ePosSplit)  
         self.endPos0 = float(self.ePosSplit[0])    
         self.endPos1 = float(self.ePosSplit[1]) 
         self.endPos2 = float(self.ePosSplit[2]) 
         print("End Point (0):", self.endPos0)  
         print("End Point (1):", self.endPos1)
         print("End Point (2):", self.endPos2)
         self.bifurcationPoints2 = slicer.modules.markups.logic().AddFiducial(self.endPos0, self.endPos1, self.endPos2)
       elif self.cont != self.rows:
        #print("contador=", self.cont)
        self.startPos = self.tableNode.GetCellText((i + 1), (self.columns -2)) #get next StartPointPosition
        self.endPos = self.tableNode.GetCellText(i,(self.columns -1)) #get the EndPointPosition
        print("Start Position:", self.startPos)
        print("End Point:", self.endPos)
        if self.startPos == self.endPos:
         print("BIFURCATION FOUND!")
         self.ePosSplit = self.endPos.split()
         print("End Point (split):", self.ePosSplit)  
         self.endPos0 = float(self.ePosSplit[0])    
         self.endPos1 = float(self.ePosSplit[1]) 
         self.endPos2 = float(self.ePosSplit[2]) 
         print("End Point (0):", self.endPos0)  
         print("End Point (1):", self.endPos1)
         print("End Point (2):", self.endPos2)
         self.bifurcationPoints2 = slicer.modules.markups.logic().AddFiducial(self.endPos0, self.endPos1, self.endPos2)
     print("end of bifurcation localization #2")
    
  def onNewClicked(self):
   
    self.bifurcationPoints2 = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode')
    self.bifurcationPoints2.CreateDefaultDisplayNodes()
    self.bifurcationPoints2.SetName('Bifurcations_2')
    self.displayNode2 = self.bifurcationPoints2.GetDisplayNode()
    self.displayNode2.SetGlyphScale(2)
    self.displayNode2.SetSelectedColor(0,0,1)

#
# bifurcLogic
#

class bifurcLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("Threshold"):
      parameterNode.SetParameter("Threshold", "100.0")
    if not parameterNode.GetParameter("Invert"):
      parameterNode.SetParameter("Invert", "false")

  def process(self, inputVolume, outputVolume, imageThreshold, invert=False, showResult=True):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    :param inputVolume: volume to be thresholded
    :param outputVolume: thresholding result
    :param imageThreshold: values above/below this threshold will be set to 0
    :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
    :param showResult: show output volume in slice viewers
    """

    if not inputVolume or not outputVolume:
      raise ValueError("Input or output volume is invalid")

    import time
    startTime = time.time()
    logging.info('Processing started')

    # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
    cliParams = {
      'InputVolume': inputVolume.GetID(),
      'OutputVolume': outputVolume.GetID(),
      'ThresholdValue' : imageThreshold,
      'ThresholdType' : 'Above' if invert else 'Below'
      }
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
    # We don't need the CLI module node anymore, remove it to not clutter the scene with it
    slicer.mrmlScene.RemoveNode(cliNode)

    stopTime = time.time()
    logging.info('Processing completed in {0:.2f} seconds'.format(stopTime-startTime))

#
# bifurcTest
#

class bifurcTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear()

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_bifurc1()

  def test_bifurc1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    # Get/create input data

    import SampleData
    registerSampleData()
    inputVolume = SampleData.downloadSample('bifurc1')
    self.delayDisplay('Loaded test data set')

    inputScalarRange = inputVolume.GetImageData().GetScalarRange()
    self.assertEqual(inputScalarRange[0], 0)
    self.assertEqual(inputScalarRange[1], 695)

    outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    threshold = 100

    # Test the module logic

    logic = bifurcLogic()

    # Test algorithm with non-inverted threshold
    logic.process(inputVolume, outputVolume, threshold, True)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], threshold)

    # Test algorithm with inverted threshold
    logic.process(inputVolume, outputVolume, threshold, False)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], inputScalarRange[1])

    self.delayDisplay('Test passed')
