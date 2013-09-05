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
python dseg.py data O:\images\neuropil\data3 I:\dp2_output --zprocess --submit --sigma=4 --level=0.5 --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY --init  --seeds=[[473,44,10],[425,465,10]]
</pre>

Linux example:
<br><pre>
cd dseg<br>
python dseg.py data /home/rgiuly/output/test4 --zprocess --submit --sigma=4 --level=0.5 --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY --init  --seeds=[[473,44,10],[425,465,10]]
</pre>


parameters
==========
* --zprocess Run process for collecting decisions from users.
* --submit Submit decisions to Mechanical Turk.
* --sigma=4 Amount of blur before watershed.
* --level=0.5 Watershed level.
* --access_key=X Set to your access key from Mechanical Turk.
* --secret_key=X Set to your secret key from Mechanical Turk.
* --init Do initialization. This make take some time from a large volume.
* --seeds=[[473,44,10],[425,465,10]] Seeds where each cell should start in the form [X,Y,Z]. You can use IMOD to get the numbers.



To initially start the process from the beginning, use "--init". This will create initial superpixels (which takes a long time) and then it will start collecting decisions from users.
<pre>python dseg.py data /home/rgiuly/output/test4 --zprocess --submit --sigma=4 --level=0.5 --access_key=X --secret_key=X --init --seeds=[[473,44,10],[425,465,10]]</pre>

You can add parameters such as this. New regions will be sent to the database as they are discovered by users.
<pre>--send_regions_to_database --dataset_id=10821524 --model_id=2000</pre>


You can abort the process when results are being collected from users and pick up later.
To continue collecting, leave out --init like this:
<pre>python dseg.py data /home/rgiuly/output/test4 --zprocess --submit --sigma=4 --level=0.5 --access_key=X --secret_key=X --seeds=[[473,44,10],[425,465,10]]</pre>


If you want to delete results collected from users so far and restart collection, use the --restart option like this:
<pre>python dseg.py data /home/rgiuly/output/test4 --zprocess --submit --sigma=4 --level=0.5 --access_key=X --secret_key=X --restart --seeds=[[473,44,10],[425,465,10]]</pre>


You can manually exclude nodes from the output with --delete, for example:
--delete=[\'116_26\',\'116_14\',\'115_47\']



Creating a qualification set that will be used to train users:

<pre>python dseg.py data /home/rgiuly/output/test4 --zqual --answers=~/answers1.txt --sigma=4 --level=0.5 --access_key=X --secret_key=X</pre>



Send superpixel regions checked by users to model in SLASH portal (galle.crbs.ucsd.edu) example:

<pre>python dseg.py data /home/rgiuly/output/test4 --send_regions_to_database --dataset_id=10821524 --model_id=2000</pre>



This approves submitted tasks, which allows Mechanical Turk users to be paid.

<pre>dseg.py data /home/rgiuly/output/test4 --approve_all --access_key=X --secret_key=X</pre>



<a href=http://bioinformatics.oxfordjournals.org/content/29/10/1359> DP2: Distributed 3D Image Segmentation Using Micro-labor Workforce </a>



