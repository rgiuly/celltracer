celltracer
==========

![Alt attribute text Here](doc/dp2.gif)


Traces cells through 3D electron microscopy images with help from Mechanical Turk users. See connectomics.


This is a new program and not fully written yet but it can be used.

A "data" directory with an example stack of images is included with the code for demonstration.


Windows example:
<code>python data O:\images\neuropil\data3 I:\dp2_output --zprocess --submit --sigma=4 --level=0.5</code>

Linux example:
<code>python data /home/rgiuly/output/paper_cerebellum --zprocess --submit --sigma=4 --level=0.5</code>


This bit of the code in dseg.py controls what processes will run:
<pre>
            if 0: initializeVolumes()
            if 0: initializeZEdges()
            if 0: makeAllRegions(initialSegFolder, inputFileExtension=inputFileExtension)
            if 0: renderAllRegions(loadImageStack(inputStack, None), 1)
            if 0: initializeRequestLoop()
            if 1: requestLoop()
</pre>

Set all to 1 (true) to run all steps. That's what you do to initalize the process.


You can run with just requestLoop() after the initialization completes one time. This is how you would typically recover/continue the process of collecting answers from mechnical turk users.

