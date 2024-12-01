python early:
    renpy.register_shader(
        "onigiri_dickcasting",

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

            float capIntersect( in vec3 ro, in vec3 rd, in vec3 pa, in vec3 pb, in float r )
            {
                vec3  ba = pb - pa;
                vec3  oa = ro - pa;

                float baba = dot(ba,ba);
                float bard = dot(ba,rd);
                float baoa = dot(ba,oa);
                float rdoa = dot(rd,oa);
                float oaoa = dot(oa,oa);

                float a = baba      - bard*bard;
                float b = baba*rdoa - baoa*bard;
                float c = baba*oaoa - baoa*baoa - r*r*baba;
                float h = b*b - a*c;
                if( h>=0.0 )
                {
                    float t = (-b-sqrt(h))/a;
                    float y = baoa + t*bard;
                    // body
                    if( y>0.0 && y<baba ) return t;
                    // caps
                    vec3 oc = (y<=0.0) ? oa : ro - pb;
                    b = dot(rd,oc);
                    c = dot(oc,oc) - r*r;
                    h = b*b - c;
                    if( h>0.0 ) return -b - sqrt(h);
                }
                return -1.0;
            }

            vec3 capNormal( in vec3 pos, in vec3 a, in vec3 b, in float r )
            {
                vec3  ba = b - a;
                vec3  pa = pos - a;
                float h = clamp(dot(pa,ba)/dot(ba,ba),0.0,1.0);
                return (pa - h*ba)/r;
            }

            float dot2( in vec3 v ) { return dot(v,v); }

            vec4 coneIntersect(in vec3 ro, in vec3 rd, in vec3 pa, in vec3 pb, in float ra, in float rb )
            {
                vec3  ba = pb - pa;
                vec3  oa = ro - pa;
                vec3  ob = ro - pb;
                float m0 = dot(ba,ba);
                float m1 = dot(oa,ba);
                float m2 = dot(rd,ba);
                float m3 = dot(rd,oa);
                float m5 = dot(oa,oa);
                float m9 = dot(ob,ba); 
                
                // caps
                if( m1<0.0 )
                {
                    if( dot2(oa*m2-rd*m1)<(ra*ra*m2*m2) ) // delayed division
                        return vec4(-m1/m2,-ba*inversesqrt(m0));
                }
                else if( m9>0.0 )
                {
                    float t = -m9/m2;                     // NOT delayed division
                    if( dot2(ob+rd*t)<(rb*rb) )
                        return vec4(t,ba*inversesqrt(m0));
                }
                
                // body
                float rr = ra - rb;
                float hy = m0 + rr*rr;
                float k2 = m0*m0    - m2*m2*hy;
                float k1 = m0*m0*m3 - m1*m2*hy + m0*ra*(rr*m2*1.0        );
                float k0 = m0*m0*m5 - m1*m1*hy + m0*ra*(rr*m1*2.0 - m0*ra);
                float h = k1*k1 - k2*k0;
                if( h<0.0 ) return vec4(-1.0); //no intersection
                float t = (-k1-sqrt(h))/k2;
                float y = m1 + t*m2;
                if( y<0.0 || y>m0 ) return vec4(-1.0); //no intersection
                return vec4(t, normalize(m0*(m0*(oa+t*rd)+rr*ba*ra)-ba*hy*y));
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

                //----------------------------------------------
                vec3 spherePos = vec3(.0, -1.75, -1.0);
                it = sphIntersect(ro, rd, spherePos, 2.0);
                if(it.x > 0.0 && it.x < minIt.x) {
                    minIt = it;
                    vec3 itPos = ro + rd * it.x;
                    n = normalize(itPos - spherePos);
                    col = vec3(1.0, 0.2, 0.1);
                }

                spherePos = vec3(.0, 1.75, -1.0);
                it = sphIntersect(ro, rd, spherePos, 2.0);
                if(it.x > 0.0 && it.x < minIt.x) {
                    minIt = it;
                    vec3 itPos = ro + rd * it.x;
                    n = normalize(itPos - spherePos);
                    col = vec3(1.0, 0.2, 0.1);
                }

                float capHeight = 10.0;
                float capRad = 1.5;                
                vec3 capPos = vec3(1.5, .0, -capHeight / 2.0 - capRad);
                vec3 capStart = capPos + vec3(.0, .0, -capHeight/2.0);
                vec3 capEnd = capPos + vec3(.0, .0, capHeight/2.0);

                it = vec2(capIntersect(ro, rd, capStart, capEnd, capRad));
                if(it.x > 0.0 && it.x < minIt.x) {
                    minIt = it;
                    vec3 itPos = ro + rd * it.x;
                    n = normalize(capNormal(itPos, capStart, capEnd, capRad));
                    col = vec3(1.0, 0.2, 0.1);
                }

                vec3 coneStart = capStart;// vec3(5.0, 5.0, -1.0);
                vec3 coneEnd = capStart - vec3(.0, .0, 5.0);
                float coneRad = capRad * 1.5;
                it = coneIntersect(ro, rd, coneStart, coneEnd, coneRad, .0).xy;
                if(it.x > 0.0 && it.x < minIt.x) {
                    minIt = it;
                    vec3 itPos = ro + rd * it.x;
                    n = normalize(coneIntersect(ro, rd, coneStart, coneEnd, coneRad, .0).yzw);
                    col = vec3(1.0, 0.2, 0.1);
                }

                
                
                //----------------------------------------------

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