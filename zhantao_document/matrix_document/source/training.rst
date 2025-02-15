Training
------------------------------
The full training process of our model is divided into four stages:
1. LoRA Fine-Tuning: Fine-tuning the original CogVideoX-2B model with LoRA to enable it to generate game scenes.
2. Adding the Interactive Module: Training the model to generate videos based on user input control signals.
3. Apply Swin-DPM: Apply the Swin-DPM algorithm described in the paper, enabling the model to generate videos of unlimited length.
4. SCM Training: Training the model with SCM to accelerate inference speed to real-time.
Training details of each stage are shown as follows.

Stage1: LoRA Fine-Tuning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Training script
Firstly,  set base model and data root arguments in stage1/training/lora_config.py, especially the following three arguments:

.. code-block:: python

   args.pretrained_model_name_or_path = "path/to/model"   # str: Path to pretrained model or model identifier from huggingface.co/models.
   args.data_root = "path/to/data_root"  # Path to root folder of videos.
   args.index_file = "path/to/index_file"  # Path to training data index file.

The pretrained_model_name_or_path is the path of the original CogVideoX-2B model, or huggingface identifier. All data can be found in our GitHub repo.
Also, don't forget to set GPU information in stage1/train_text_to_video_lora.sh.
After setting up all arguments, run training with:
::
   cd stage1
   bash train_text_to_video_lora.sh
To customize your training, feel free to modify training arguments.
Notes
After the training is finished, you need to fuse LoRA parameters into the base model for the next stage of training.
We provide a script stage1/fuse_lora_weights.py to achieve this. It's quite easy to use with only three arguments to set.
You can also check model performance by generating videos with stage1/inference.py

Stage2: Adding the Interactive Module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Training script
Similarly, first set necessary arguments in stage2/training/sft_config.py and stage2/train_text_to_video_sft.sh. Note that the args.pretrained_model_name_or_path should be the output_dir of stage1/fuse_lora_weights.py.
Then run:
::

   cd stage2
   bash train_text_to_video_sft.sh
Notes
In this stage, only parameters in the Interactive Module (i.e. control_adapter module) are trainable.

Stage3: Apply Swin-DPM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Similarly, first set necessary arguments in stage3/training/sft_config.py and stage3/train_text_to_video_sft.sh.
Then run:
::

   cd stage3
   bash train_text_to_video_sft.sh
Notes
This stage applies full-parameter finetuning. Please take care of training parameters to avoid OOM.
This stage involves extensive code modifications, particularly in pipeline_cogvideox.py and scheduler.py. After this stage, you should be able to generate 1 min interactive video using time less than 16 min on a single Nvidia A100 GPU. Further acceleration from SCM and parallel sampling will improve the inference speed to real-time.

Stage4: SCM Training
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO