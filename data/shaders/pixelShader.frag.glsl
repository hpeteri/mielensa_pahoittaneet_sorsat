#version 330

uniform sampler2D tex;
in vec2 pass_tc;
in vec4 pass_col;

out vec4 frag_col;
void main(){
  frag_col = texture(tex, pass_tc) * pass_col;
}
