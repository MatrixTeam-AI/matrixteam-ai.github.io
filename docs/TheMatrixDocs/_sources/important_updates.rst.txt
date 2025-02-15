Important updates
------------------------------
According to a request from Alibaba Tongyi Lab, the previous version of The Matrix was inherited from an internal version of Video DiT and could not be openly released. Therefore, we have re-implemented The Matrix code based on the previously open-released video generation model, CogVideoX. We sincerely appreciate the efforts of the CogVideo team for their contributions.

As a result, the open release of our model has been delayed, and some components are still under development. These components will be released as soon as they are finished, including:

- [ ] Inference scripts for 8-GPU parallel inference of the DiT backbone, which will accelerate the inference speed by around 6-8 times.
- [ ] Training of the Stream Consistency Models, which will accelerate inference speed by around 7-10 times.
- [ ] Training on fused realistic and simulated data to acquire stronger generalization ability.