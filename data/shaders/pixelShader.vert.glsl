#version 330

uniform mat4 projection = mat4(1, 0, 0, 0,
                               0, 1, 0, 0,
                               0, 0, 1, 0,
                               0, 0, 0, 1);

layout (location = 0) in vec2 position;
layout (location = 1) in vec2 tc;

layout (location = 2) in vec4 model_mat_col_0;
layout (location = 3) in vec4 model_mat_col_1;
layout (location = 4) in vec4 model_mat_col_2;
layout (location = 5) in vec4 model_mat_col_3;  
layout (location = 6) in vec4 col;

out vec4 pass_col;
out vec2 pass_tc;

void main(void){
  gl_Position = projection * mat4(model_mat_col_0,
                                  model_mat_col_1,
                                  model_mat_col_2,
                                  model_mat_col_3) * vec4(position, 0, 1);
  pass_tc = tc;
  pass_col = col / 255;
                  
 
}
