init 2 python:
    import pygame
    import math

    class OnigiriShaderDisp(renpy.Displayable):
        default_controls = {
            "FORWARD": pygame.K_w,
            "BACKWARD": pygame.K_s,
            "STRAFE_LEFT": pygame.K_a,
            "STRAFE_RIGHT": pygame.K_d,
            "JUMP": pygame.K_SPACE,
            "DUCK": pygame.K_LSHIFT,
            }

        def __init__(self, **d_props):
            super().__init__(**d_props)
            self.oldst = .0
            self.camera_rot = vec2()
            self.camera_pos = vec3(-5.0, .0, .0)
            self.movement_speed = 5.0

            self.keymap = {key: False for key in (self.default_controls["FORWARD"],
                                                  self.default_controls["BACKWARD"],
                                                  self.default_controls["STRAFE_LEFT"],
                                                  self.default_controls["STRAFE_RIGHT"],
                                                  self.default_controls["JUMP"],
                                                  self.default_controls["DUCK"])}

            

        def event(self, ev, x, y, st):
            if ev.type == pygame.KEYDOWN and ev.key in self.keymap:
                self.keymap[ev.key] = True
                raise renpy.IgnoreEvent()

            elif ev.type == pygame.KEYUP and ev.key in self.keymap:
                self.keymap[ev.key] = False
                raise renpy.IgnoreEvent()

            if ev.type == pygame.MOUSEMOTION:
                pass

        def render(self, w, h, st, at):
            dt = self.oldst - st 
            self.oldst = st

            center = vec2(w, h) / 2.0
            mouse_rel = (center - vec2(*pygame.mouse.get_pos())) * 0.01
            self.camera_rot -= mouse_rel
            self.camera_rot %= math.tau

            pygame.mouse.set_pos(center)

            direction = vec3()
            temp_direction = vec3()
            if self.keymap[self.default_controls["FORWARD"]]:
                direction += (-1.0, .0, .0)
            if self.keymap[self.default_controls["BACKWARD"]]:
                direction += (1.0, .0, .0)
            if self.keymap[self.default_controls["STRAFE_LEFT"]]:
                direction += (.0, 1.0, .0)
            if self.keymap[self.default_controls["STRAFE_RIGHT"]]:
                direction += (.0, -1.0, .0)
            if self.keymap[self.default_controls["JUMP"]]:
                direction += (.0, .0, 1.0)
            if self.keymap[self.default_controls["DUCK"]]:
                direction += (.0, .0, -1.0)

            temp_direction.zxy = vec3(direction.z * math.cos(-self.camera_rot.y) - direction.x * math.sin(-self.camera_rot.y),
                                      direction.z * math.sin(-self.camera_rot.y) + direction.x * math.cos(-self.camera_rot.y),
                                      direction.y)

            direction = vec3(temp_direction.x * math.cos(self.camera_rot.x) - temp_direction.y * math.sin(self.camera_rot.x),
                             temp_direction.x * math.sin(self.camera_rot.x) + temp_direction.y * math.cos(self.camera_rot.x),
                             temp_direction.z)


            print(self.camera_pos, direction, self.movement_speed, dt)
            self.camera_pos += direction * self.movement_speed * dt



            rv = renpy.Render(w, h)

            # Дополнительный рендер под шейдер
            shader_rend = renpy.Render(w, h)
            shader_rend.fill("#000")
            shader_rend.mesh = True
            shader_rend.add_shader("onigiri_raycasting")
            shader_rend.add_uniform("u_resolution", (w, h))
            shader_rend.add_uniform("u_time", st)
            shader_rend.add_uniform("u_rot", self.camera_rot)
            shader_rend.add_uniform("u_pos", self.camera_pos)

            rv.blit(shader_rend, (0, 0))
            rv.blit(Text(str(self.keymap).replace("{", "(").replace("}", ")")).render(w, h, st, at), (0, 0))
            rv.blit(Text(str((w, h))).render(w, h, st, at), (0, 36))
            rv.blit(Text(str(self.camera_rot)).render(w, h, st, at), (0, 72))
            rv.blit(Text(str(self.camera_pos)).render(w, h, st, at), (0, 36*3))

            renpy.redraw(self, .0)
            return rv

screen onigiri():
    default gameObj = OnigiriShaderDisp()

    add gameObj:
        xysize 1.0, 1.0