Inference
------------------------------
We provide the the_matrix class as an interface for users to easily generate interactive worlds. The related code can be found in the_matrix.py.
We also offer a generation example script generation_example.py in the root dir.

.. code-block:: python

   from the_matrix import the_matrix

   the_matrix_generator = the_matrix(generation_model_path="path/to/stage2_model", streaming_model_path="path/to/stage3_model")
   the_matrix_generator.generate(
      prompt="...",
      length=8,
      output_folder="./",
      control_signal="..."
   )

generation_model_path and streaming_model_path are the stage2 and stage3 models we provide.
Note that the control_signal parameter can be set to None. In this case, the code will generate a random control signal to be used for video generation.
Detailed parameter descriptions are as follows:
::

   prompt:
      The description of the video to be generated.
   length:
      Length in second of generated video.
   control_signal:
      Control signal for generated video, like "D,D,D,D,D,DL,DL,DL,DL,D,D,D,DR,DR,DR,DR,DR".
      Meanings:
         "D": The car is moving straight ahead.
         "DL": The car is turning left ahead.
         "DR": The car is turning right ahead.
      For input, if it's length is less than 4 * length + 1, it will be randomly padded.
      Leave it to None for random generation.
   control_seed:
      If control_signal is None, this seed determines the random generated control signal.
   output_folder:
      Folder path for saving generated videos.
   guidance_scale:
      CFG parameter. Leave it to default is good enough.
   seed:
      Random seed for video generation.
   gpu_id:
      The index of GPU to be used.
      
The generation function in the_matrix calls inference.py within the respective stage folders. For more detailed generation settings, you can use the corresponding scripts in those folders.

Here 'D' stands for 'The car is Driving forward' which corresponds to pressing the 'W' key on the keyboard, 'DL' stands for 'The car is Driving Left' and corresponds to pressing the 'A' key, 'DR' stands for 'The car is Driving Right' and corresponds to pressing the 'D' key.

