##############################
# File :: matrix.py
# Written on Saturday,  4 September 2021.
# Author: Henrik Peteri
##############################
import math

def Translate(x, y, z) -> list:
    return [1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            x, y, z, 1]

def Scale(x,y,z) -> list:
    return [x, 0.0, 0.0, 0.0,
            0.0, y, 0.0, 0.0,
            0.0, 0.0, z, 0.0,
            0.0, 0.0, 0.0, 1.0]

def RotateZ(rad) -> list:
    return [math.cos(rad), math.sin(rad), 0.0, 0.0,
            -1.0 * math.sin(rad), math.cos(rad), 0.0, 0.0,
            0.0,  0.0,1.0, 0.0,
            0.0,  0.0, 0.0, 1.0]
 
def Orthographic(left, right, top, bottom, ne, fa) -> list:
     return [2.0 / (right - left), 0.0, 0.0, 0.0,
             0.0, 2.0 / (top - bottom), 0.0, 0.0,
             0.0, 0.0, 2.0 / (fa - ne), 0.0,
             (-(right + left) / (right - left)), (-(top + bottom) / (top - bottom)), (-(fa + ne) / (fa - ne)), 1.0]
 
def Mul_Vec_Mat(vec, mat) -> list:    
    return [mat[0] * vec[0] + mat[4] * vec[1] + mat[8] * vec[2] + mat[12] * vec[3],
            mat[1] * vec[0] + mat[5] * vec[1] + mat[9] * vec[2] + mat[13] * vec[3],
            mat[2] * vec[0] + mat[6] * vec[1] + mat[10] * vec[2] + mat[14] * vec[3],
            mat[3] * vec[0] + mat[7] * vec[1] + mat[11] * vec[2] + mat[15] * vec[3]]

def Mul_Mat_Mat(mat0, mat1) -> list:
    result = [0] * 16
  
    for c in range(4):
      for r in range(4):
          for i in range(4):
              result[c * 4 + r] += mat0[i * 4 + r] * mat1[c * 4 + i]

    return result

def GetModelMatrix(x, y, scale_x, scale_y, rot_z):
    model = Mul_Mat_Mat(RotateZ(rot_z), Scale(scale_x, scale_y, 1))
    model = Mul_Mat_Mat(Translate(x, y, 1), model)
    return model
      
def PrintMatrix(mat):
    print("_________")
    for r in range(4):
        print("[{} {} {} {}]".format(mat[r], mat[4 + r], mat[8 + r], mat[12 + r]))
    print("---------")
