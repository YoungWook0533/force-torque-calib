# force-torque-calib
Force/Torque sensor calibration using LSM.

## Usage
- Measure f/t sensor value at 24 sensor frame oreintations.
[Paper](https://www.researchgate.net/publication/253989945_Bias_Estimation_and_Gravity_Compensation_For_Force-Torque_Sensors?enrichId=rgreq-b2611e2d533d22fac6875a7f58d47403-XXX&enrichSource=Y292ZXJQYWdlOzI1Mzk4OTk0NTtBUzoxMDIzNjY2NzgzNTU5NzRAMTQwMTQxNzUyNjQxOQ%3D%3D&el=1_x_3)
```bash
python3 ft_calib.py /path/to/your/sensor_data.txt
```