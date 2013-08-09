celltracer
==========

![Alt attribute text Here](doc/dp2_300x300.gif)
![Alt attribute text Here](doc/movie_of_gial_cell_and_neuron_smaller.gif)


Traces cells through 3D electron microscopy images with help from Mechanical Turk users. See connectomics.


This is a new program and not fully written yet but it can be used.

A "data" directory with an example stack of images is included with the code for demonstration.


Windows example:
<br><pre>
cd dseg<br>
python dseg.py data O:\images\neuropil\data3 I:\dp2_output --zprocess --submit --sigma=4 --level=0.5 --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY
</pre>

Linux example:
<br><pre>
cd dseg<br>
python dseg.py data /home/rgiuly/output/paper_cerebellum --zprocess --submit --sigma=4 --level=0.5 --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY
</pre>


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


<a href=http://bioinformatics.oxfordjournals.org/content/29/10/1359> DP2: Distributed 3D Image Segmentation Using Micro-labor Workforce </a>
