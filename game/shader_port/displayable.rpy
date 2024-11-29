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
            self.camera_rot = vec2(.0)
            self.camera_pos = vec3(-5.0, .0, .0)
            self.movement_speed = 5.0

            self.keymap = {key: False for key in (self.default_controls["FORWARD"],
                                                  self.default_controls["BACKWARD"],
                                                  self.default_controls["STRAFE_LEFT"],
                                                  self.default_controls["STRAFE_RIGHT"],
                                                  self.default_controls["JUMP"],
                                                  self.default_controls["DUCK"])}

            self.pano = renpy.displayable("panorama.jpg")

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

            #if renpy.display.interface.

            center = vec2(w, h) / 2.0
            mouse_rel = (center - vec2(*pygame.mouse.get_pos())) * 0.01
            old_yaw = self.camera_rot.y
            self.camera_rot -= mouse_rel
            self.camera_rot %= math.tau    
            #renpy.display.interface.set_mouse_pos(*center, 1.0)        
            pygame.mouse.set_pos(center)

            # Защита от сальтух
            cor_rot = (self.camera_rot.y+math.pi)%math.tau
            if cor_rot > math.tau - math.pi / 2:
                self.camera_rot.y = old_yaw                
            elif cor_rot < math.pi / 2:
                self.camera_rot.y = old_yaw

            # Направление движения
            direction = vec3()
            temp_direction = vec3()
            if self.keymap[self.default_controls["FORWARD"]]: direction.x += -1.0
            if self.keymap[self.default_controls["BACKWARD"]]: direction.x += 1.0
            if self.keymap[self.default_controls["STRAFE_LEFT"]]: direction.y += 1.0
            if self.keymap[self.default_controls["STRAFE_RIGHT"]]: direction.y += -1.0
            if self.keymap[self.default_controls["JUMP"]]: direction.z += 1.0
            if self.keymap[self.default_controls["DUCK"]]:    direction.z += -1.0

            temp_direction.zxy = vec3(direction.z * math.cos(-self.camera_rot.y) - direction.x * math.sin(-self.camera_rot.y),
                                      direction.z * math.sin(-self.camera_rot.y) + direction.x * math.cos(-self.camera_rot.y),
                                      direction.y)

            direction = vec3(temp_direction.x * math.cos(self.camera_rot.x) - temp_direction.y * math.sin(self.camera_rot.x),
                             temp_direction.x * math.sin(self.camera_rot.x) + temp_direction.y * math.cos(self.camera_rot.x),
                             temp_direction.z)

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

            pano_rend = renpy.render(self.pano, w, h, st, at)
            pano_rend = pano_rend.render_to_texture()
            shader_rend.add_uniform("tex1", pano_rend)

            rv.blit(shader_rend, (0, 0))
            rv.blit(Text(f"pos: {round(self.camera_pos,3)}").render(w, h, st, at), (0, 0))
            rv.blit(Text(f"pitch: {round(self.camera_rot.x, 3)} yaw: {round((self.camera_rot.y+math.pi)%math.tau, 3)}").render(w, h, st, at), (0, 36))

            renpy.redraw(self, .0)
            return rv

screen onigiri():
    default gameObj = OnigiriShaderDisp()

    add gameObj:
        xysize 1.0, 1.0
        align .5, .5