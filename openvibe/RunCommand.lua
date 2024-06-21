-- this function is called when the box is initialized
function initialize(box)
end

-- this function is called when the box is uninitialized
function uninitialize(box)
	io.write("uninitialize has been calle d\n")
end

function process(box)
	box:send_stimulation(1,33084,0.2,0) --Start LSL communication
	box:sleep()
	io.write("process has been called\n")

end