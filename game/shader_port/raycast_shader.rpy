﻿python early:
    renpy.register_shader(
        "onigiri_raycasting",

        variables="""
            uniform vec2 u_rot;
            uniform vec3 u_pos;
            uniform vec2 u_resolution;
            uniform vec2 u_model_size;
            attribute vec2 a_tex_coord;
            varying vec2 v_tex_coord;
            varying vec2 v_pix_size;
        """,


        vertex_300="""
            v_tex_coord = a_tex_coord;
            v_pix_size = 1.0 / u_model_size;
        """,

        fragment_functions="""
            const float MAX_DIST = 99999.0;
            vec3 light = normalize(vec3(.85, -.75, -.75));            
            uniform sampler2D tex1;

            mat2 rot(in float a) {
                float s = sin(a);
                float c = cos(a);
                return mat2(c, -s, s, c);
            }

            vec2 sphIntersect( in vec3 ro, in vec3 rd, in vec3 ce, float ra )
            {
                vec3 oc = ro - ce;
                float b = dot( oc, rd );
                float c = dot( oc, oc ) - ra*ra;
                float h = b*b - c;
                if(h < 0.0 ) return vec2(-1.0); // no intersection
                h = sqrt( h );
                return vec2( -b-h, -b+h );
            }

            vec2 boxIntersection( in vec3 ro, in vec3 rd, vec3 boxSize, out vec3 outNormal ) 
            {
                vec3 m = 1.0 / rd;
                vec3 n = m * ro;
                vec3 k = abs(m) * boxSize;
                vec3 t1 = -n - k;
                vec3 t2 = -n + k;
                float tN = max(max(t1.x, t1.y), t1.z);
                float tF = min(min(t2.x, t2.y), t2.z);
                if(tN>tF || tF<0.0) return vec2(-1.0);
                outNormal = -sign(rd) * step(t1.yzx, t1.xyz) * step(t1.zxy, t1.xyz);
                return vec2( tN, tF );
            }

            vec2 plaIntersect(in vec3 ro, in vec3 rd, in vec4 p) {
                return vec2(-(dot(ro, p.xyz) + p.w) / dot(rd, p.xyz));
            }

            vec3 getSky(in vec3 rd) {
                vec2 uv = vec2(atan(rd.x, rd.y), asin(rd.z) * 2.0);
                uv /= 3.14159265;
                uv = uv * .5 + .5;

                vec3 col = vec3(0.6,0.75,0.85) - 1.25*uv.y;
                vec3 sun = vec3(0.95, 0.9, 1.0);

                sun *= pow(max(0.0, dot(rd, light)), 32.0);
                col = clamp(sun + col, 0.0, 1.0);
                return col;
            }

            vec3 castRay(inout vec3 ro, inout vec3 rd) {
                vec3 col;
                vec2 minIt = vec2(MAX_DIST);
                vec2 it;
                vec3 n;

                vec3 spherePos = vec3(.0, -1.5, .0);
                it = sphIntersect(ro, rd, spherePos, 1.0);
                if(it.x > 0.0 && it.x < minIt.x) {
                    minIt = it;
                    vec3 itPos = ro + rd * it.x;
                    n = normalize(itPos - spherePos);
                    col = vec3(1.0, 0.2, 0.1);
                }

                vec3 boxN;
                vec3 boxPos = vec3(0.0, 1.5, .0);
                it = boxIntersection(ro - boxPos, rd, vec3(1.0), boxN);
                if(it.x > 0.0 && it.x < minIt.x) {
                    minIt = it;
                    n = normalize(boxN);
                    col = vec3(0.4, 0.6, 0.8);
                }
               
                vec3 planeNormal = vec3(0.0, 0.0, -1.0);
                it = plaIntersect(ro, rd, vec4(planeNormal, 1.0));
                if(it.x > 0.0 && it.x < minIt.x) {
                    minIt = it;
                    n = normalize(planeNormal);
                    col = vec3(.75, .75, .75);
                }

                if(minIt.x == MAX_DIST) return vec3(-1.0);                
                float diffuse = dot(light, n) * 0.5 + 0.5;
                float specular = pow(max(0.0, dot(reflect(rd, n), light)), 32.0) * 2.0;
                col *= mix(diffuse, specular, 0.5);
                col = mix(col, getSky(rd), 1.0 - exp(-0.0001 * dot(minIt, vec2(1.0)) * dot(minIt, vec2(1.0))));
                ro += rd * (minIt.x - 0.001);
                rd = n;
                return col;
            }

            vec3 traceRay(in vec3 ro, in vec3 rd) {
                vec3 col = castRay(ro, rd);
                if(col.x < 0.0) return getSky(rd);
                vec3 lightDir = light;
                if(dot(rd, light) > 0.0) {
                    if(castRay(ro, lightDir).x != -1.0) col *= 0.5;
                }
                return col;
            }

        """,

        fragment_300="""
            vec2 uv = (v_tex_coord - 0.5) * u_resolution / u_resolution.y;
            vec3 rayOrigin = u_pos;
            vec3 rayDirection = normalize(vec3(1.0, uv));
            rayDirection.zx *= rot(-u_rot.y);
            rayDirection.xy *= rot(u_rot.x);
            vec3 col = traceRay(rayOrigin, rayDirection);
            col.r = pow(col.r, 0.45);
            col.g = pow(col.g, 0.45);
            col.b = pow(col.b, 0.45);
            gl_FragColor = vec4(col, 1.0);
        """,)