# deeparc file format specification

## file structure

```
<deeparc_version> 
<number_point2d> <number_instrinsic> <number_extrinsic_on_arc> <number_extrinsic_on_ring> <number_point3d>
<instrinsic_id_1/position_on_arc> <extrinsic_id_1/position_on_ring> <point3d_id_1> <point2d_x_1> <point2d_y_1>
.
.
// repeat line until <number of 2d point>
.
.
<center_x> <center_y>  <num_of_focal_length> <focal_length_0> <focal_length_1> ... <num_of_distortion> <distrotion_0> <distrotion_1>
.
.
// repeat line until <number_instrinsic>
.
.
<translation_x> <translation_y> <translation_z> <number_rotation> <rotation_0> <rotation_1> ...  
.
.
// repeat line until <number_extrinsic>
.
.
<point3d_x> <point3d_y> <point3d_z> <point3d_r> <point3d_g> <point3d_b>
.
.
// repeat line until <number_point3d>
.
.
.
```

### variable

| variable | primative | meaning |
| -------------- | ------------- | --------- |
| deeparc_version | float | version number of deeparc, **always** place at top for software compatibility | 
| number_point2d | int | number of point2d line in this file |
| number_instrinsic | int | number of instrinsic line in this file |
| number_extrinsic_on_arc | int | number of extrinsic line in this file |
| number_extrinsic_on_ring | int | extrinsic in column, set to 0 if don't want to share extrinsic |
| number_point3d | int | number of point3d line in this file |
| instrinsic_id_1 | int | reference id to intrinsic line, index start from 0 |
| extrinsic_id_1 | int | reference id to extrinsic line, index start from 0 |
| point3d_id_1 | int | reference id to point3d line, index start from 0  |
| point2d_x_1 | float | point2d x-axis position after projected |
| point2d_y_1 | float | point2d x-axis position after projected |
| center_x | float | principle point of camera in x-axis |
| center_y | float | principle point of camera in x-axis |
| num_of_focal_length | int | number of focal length in each intrinsic should be 1 or 2, 1 if it same focal length in both x and y and 2 if focal length is difference in each axis |
| focal_length_0 | float | focal length in x axis |
| focal_length_1 | float | focal lenth in y axis (if provide) |
| num_of_distortion | int | number of distrotion, can be 0 if not have distrotion or 1, and 2 |
| distrotion_0 | int | first distrotion (if any) |
| distrtion_1 | int | second distrotion (if any) such as radial distrotion |
| translation_x | float | extrinsic translation in x axis | 
| translation_y | float | extrinsic translation in y axis | 
| translation_z | float | extrinsic translation in z axis | 
| number_rotation | int | number of rotation item in each extrinsic, can be 3 for [rotvec](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_rotvec.html#scipy.spatial.transform.Rotation.from_rotvec), 4 for [quaternions](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.as_quat.html#scipy.spatial.transform.Rotation.as_quat) in x,y,z,w format and 9 for [rotation matrix](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.as_matrix.html#scipy.spatial.transform.Rotation.as_matrix) |
| rotation_* | float | rotation info can be 3 float, 4 float or 9 float depend on number_rotation |
| point3d_x | float | x axis of point3d |
| point3d_y | float | y axis of point3d |
| point3d_z | float | z axis of point3d |
| point3d_r | int | r color [0-255] of poin3d|
| point3d_g | int | g color [0-255] of poin3d |
| point3d_b | int | b color [0-255] of poin3d |
## Example file
- Soon
