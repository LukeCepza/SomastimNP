import sys; sys.path.append('./pylsl')
# from pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet
import serial

class MyOVBox(OVBox):
   def __init__(self):
      OVBox.__init__(self)
      self.Port = 'COM1'

   def initialize(self):
      self.Port = str(self.setting['Port'])
      self.arduino=serial.Serial(self.Port,baudrate=500000)
      print(self.arduino)
      return

   def process(self):
      for chunkIndex in range( len(self.input[0]) ):
        chunk = self.input[0].pop()
        if(type(chunk) == OVStimulationSet):
            # We move through all the stimulation received in the StimulationSet and
            # we print their date and identifier
            for stimIdx in range(len(chunk)):
                stim=chunk.pop()
                self.arduino.write(str(stim.identifier).encode('utf-8'))
                print ('At time ', stim.date, ' received stim ', stim.identifier)
        else:
                print ('Received chunk of type ', type(chunk), " looking for StimulationSet")

      return

   def uninitialize(self):
      self.arduino.close()
      return

box = MyOVBox()